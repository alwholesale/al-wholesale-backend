from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'product_id', 'product_details', 'quantity')

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    cart_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'cart_total')

    # 🚀 SMART PRICING: Calculate total using bulk_price if quantity >= MOQ
    def get_cart_total(self, obj):
        total = 0
        for item in obj.items.all():
            product = item.product
            price_to_use = product.unit_price
            
            if product.bulk_price and item.quantity >= product.min_order_quantity:
                price_to_use = product.bulk_price
                
            total += price_to_use * item.quantity
        return total


class VendorOrderItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    buyer_email = serializers.CharField(source='order.user.email', read_only=True)
    shipping_address = serializers.CharField(source='order.shipping_address', read_only=True)
    order_date = serializers.DateTimeField(source='order.created_at', read_only=True, format="%Y-%m-%d %H:%M")
    product_name = serializers.CharField(source='product.name', read_only=True) # For Payouts UI

    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'buyer_email', 'shipping_address', 'order_date', 'product_name', 'product_details', 'quantity', 'price', 'total', 'status', 'platform_fee', 'vendor_earning', 'payout_status')


class BuyerOrderItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product_details', 'quantity', 'price', 'total', 'status')


class BuyerOrderSerializer(serializers.ModelSerializer):
    items = BuyerOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'shipping_address', 'billing_address', 'payment_method', 
                  'subtotal', 'tax_amount', 'total_amount', 'status', 'created_at', 'items')


# 🚀 ELITE FIX: The Missing Serializer
class OrderSerializer(serializers.ModelSerializer):
    items = BuyerOrderItemSerializer(many=True, read_only=True)
    buyer_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'buyer_name', 'shipping_address', 'billing_address', 'payment_method', 
                  'subtotal', 'tax_amount', 'total_amount', 'status', 'created_at', 'items')