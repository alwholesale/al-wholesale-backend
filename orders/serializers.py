from rest_framework import serializers
from .models import Cart, CartItem, OrderItem, Order
from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    # Cart item  ke sath product ki puri detailed bhejne ke liye...
    
    product_details = ProductSerializer(source='product', read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_details', 'quantity']
        
        
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    cart_total = serializers.SerializerMethodField()
    
    class Meta :
        model = Cart
        fields = ['id', 'user', 'items', 'cart_total', 'created_at']
        
    # total cart value calculate karne ka logic yaha per hain:
    def get_cart_total(self, obj):
        total = sum(item.product.unit_price * item.quantity for item in obj.items.all())
        return total

class VendorOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    # product.image ko string format me lene ke liye
    product_image = serializers.ImageField(source='product.image', read_only=True) 
    buyer_name = serializers.CharField(source='order.user.username', read_only=True)
    buyer_email = serializers.CharField(source='order.user.email', read_only=True)
    shipping_address = serializers.CharField(source='order.shipping_address', read_only=True)
    payment_method = serializers.CharField(source='order.payment_method', read_only=True)
    order_date = serializers.DateTimeField(source='order.created_at', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'product_name', 'product_image', 'quantity', 
            'price', 'total', 'status', 'buyer_name', 'buyer_email', 
            'shipping_address', 'payment_method', 'order_date'
        ]



class BuyerOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'product_image', 'quantity', 'price', 'total', 'status']

class BuyerOrderSerializer(serializers.ModelSerializer):
    items = BuyerOrderItemSerializer(many=True, read_only=True) # Order ke andar uske items

    class Meta:
        model = Order
        fields = ['id', 'subtotal', 'tax_amount', 'total_amount', 'status', 'shipping_address', 'payment_method', 'created_at', 'items']

