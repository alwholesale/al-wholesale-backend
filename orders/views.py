from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication # <--- YEH LINE ADD KAREIN
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
from .serializers import CartSerializer, VendorOrderItemSerializer, BuyerOrderItemSerializer, BuyerOrderSerializer
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal


class CartAPIView(APIView):
    # 🚨 YEH LINE SABSE ZAROORI HAI: Yeh Django ko CSRF block karne se rokegi
    authentication_classes = [JWTAuthentication] 
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        # ... baaki ka poora code same rahega ...
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        action = request.data.get('action')
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

        if action == 'add':
            if item_created:
                cart_item.quantity = product.min_order_quantity
            else:
                cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease':
            if cart_item.quantity > product.min_order_quantity:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        elif action == 'remove':
            cart_item.delete()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
@method_decorator(csrf_exempt, name='dispatch')
class CheckoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic 
    def post(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.all()
            
            if not cart_items.exists():
                return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

            shipping_address = request.data.get('shipping_address', '')
            billing_address = request.data.get('billing_address', '')
            payment_method = request.data.get('payment_method', 'Bank Transfer')

            subtotal = sum(item.product.unit_price * item.quantity for item in cart_items)
            from decimal import Decimal
            tax = subtotal * Decimal('0.05') 
            total_amount = subtotal + tax

            order = Order.objects.create(
                user=request.user,
                shipping_address=shipping_address,
                billing_address=billing_address,
                payment_method=payment_method,
                subtotal=subtotal,
                tax_amount=tax,
                total_amount=total_amount,
                status='pending'
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    vendor=item.product.vendor,
                    quantity=item.quantity,
                    price=item.product.unit_price,
                    total=item.product.unit_price * item.quantity,
                    status='pending'
                )

            cart.items.all().delete()

            return Response({
                "message": "Order placed successfully!", 
                "order_id": order.id
            }, status=status.HTTP_201_CREATED)

        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        


# 📦 VENDOR KE LIYE ORDERS FETCH KARNE KI API
class VendorOrderListAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Sirf wahi items laao jahan vendor = logged_in user hai
        items = OrderItem.objects.filter(vendor=request.user).order_by('-id')
        serializer = VendorOrderItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 🚚 VENDOR KE LIYE ORDER STATUS UPDATE KARNE KI API
class VendorOrderStatusUpdateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            # Security: Ensure karo ki vendor sirf apna hi order update kar paye
            item = OrderItem.objects.get(id=pk, vendor=request.user)
            new_status = request.data.get('status')
            
            if new_status in dict(OrderItem.STATUS_CHOICES).keys():
                item.status = new_status
                item.save()
                return Response({"message": f"Status updated to {new_status}"}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid status provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        except OrderItem.DoesNotExist:
            return Response({"error": "Order item not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)
        
        
        
class BuyerOrderListAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Sirf wahi orders laao jo is logged-in user ne place kiye hain
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = BuyerOrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class CartSyncAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # 1. User ka asli cart find/create karo
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # 2. Frontend se aane wale guest items ko pakdo
        guest_items = request.data.get('items', [])
        
        for item in guest_items:
            product_id = item.get('product_id')
            quantity = int(item.get('quantity', 1))
            
            try:
                product = Product.objects.get(id=product_id)
                
                # Check karo kya ye item user ke cart me pehle se hai?
                cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
                
                if item_created:
                    # Naya item hai toh directly qty set kardo (min_order check ke sath)
                    cart_item.quantity = max(quantity, product.min_order_quantity)
                else:
                    # Pehle se hai toh dono quantity merge (plus) kar do
                    cart_item.quantity += quantity
                
                cart_item.save()
                
            except Product.DoesNotExist:
                # Agar koi fake ID aaye, toh usko ignore kardo
                continue
                
        # 3. Final updated cart ka data wapas bhej do
        serializer = CartSerializer(cart)
        return Response({
            "message": "Cart synced successfully!",
            "cart": serializer.data
        }, status=status.HTTP_200_OK)