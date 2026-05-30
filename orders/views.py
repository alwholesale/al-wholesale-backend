from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal

from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
from cms.models import SiteSetting
from .serializers import (
    CartSerializer, VendorOrderItemSerializer, BuyerOrderItemSerializer, 
    BuyerOrderSerializer, OrderSerializer
)

# 🚀 ELITE FIX: Custom Master Admin Permission
class IsMasterAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin'))

class CartAPIView(APIView):
    authentication_classes = [JWTAuthentication] 
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
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
            
            settings = SiteSetting.load()
            fee_percentage = settings.platform_fee_percentage

            subtotal = Decimal('0.00')
            for item in cart_items:
                product = item.product
                price_to_use = product.unit_price
                if product.bulk_price and item.quantity >= product.min_order_quantity:
                    price_to_use = product.bulk_price
                subtotal += price_to_use * item.quantity

            tax = subtotal * Decimal('0.05') 
            total_amount = subtotal + tax

            order = Order.objects.create(
                user=request.user, shipping_address=shipping_address,
                billing_address=billing_address, payment_method=payment_method,
                subtotal=subtotal, tax_amount=tax, total_amount=total_amount, status='pending'
            )

            for item in cart_items:
                product = item.product
                price_to_use = product.unit_price
                if product.bulk_price and item.quantity >= product.min_order_quantity:
                    price_to_use = product.bulk_price
                    
                item_total = price_to_use * item.quantity
                platform_fee_amt = item_total * (fee_percentage / Decimal('100'))
                vendor_earning_amt = item_total - platform_fee_amt

                OrderItem.objects.create(
                    order=order, product=product, vendor=product.vendor,
                    quantity=item.quantity, price=price_to_use, total=item_total,
                    platform_fee=platform_fee_amt, vendor_earning=vendor_earning_amt,
                    status='pending', payout_status='pending'
                )

            cart.items.all().delete()
            return Response({"message": "Order placed successfully!", "order_id": order.id}, status=status.HTTP_201_CREATED)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        

class VendorOrderListAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        items = OrderItem.objects.filter(vendor=request.user).order_by('-id')
        serializer = VendorOrderItemSerializer(items, many=True)
        return Response(serializer.data)

class VendorOrderStatusUpdateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            item = OrderItem.objects.get(id=pk, vendor=request.user)
            new_status = request.data.get('status')
            if new_status in dict(OrderItem.STATUS_CHOICES).keys():
                item.status = new_status
                item.save()
                return Response({"message": f"Status updated to {new_status}"})
            return Response({"error": "Invalid status provided"}, status=status.HTTP_400_BAD_REQUEST)
        except OrderItem.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        
class BuyerOrderListAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = BuyerOrderSerializer(orders, many=True)
        return Response(serializer.data)
    
class CartSyncAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        guest_items = request.data.get('items', [])
        
        for item in guest_items:
            try:
                product = Product.objects.get(id=item.get('product_id'))
                cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
                if item_created:
                    cart_item.quantity = max(int(item.get('quantity', 1)), product.min_order_quantity)
                else:
                    cart_item.quantity += int(item.get('quantity', 1))
                cart_item.save()
            except Product.DoesNotExist:
                continue
                
        return Response({"message": "Cart synced!"}, status=status.HTTP_200_OK)

# ================= MASTER ADMIN ENGINES =================

class AdminAllOrdersView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsMasterAdmin] # 🚀 FIXED HERE
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer

class AdminPayoutsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsMasterAdmin] # 🚀 FIXED HERE

    def get(self, request):
        items = OrderItem.objects.all().order_by('-id')
        serializer = VendorOrderItemSerializer(items, many=True)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            item = OrderItem.objects.get(id=pk)
            item.payout_status = 'paid'
            item.save()
            return Response({"message": "Payout marked as Paid!"})
        except OrderItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)