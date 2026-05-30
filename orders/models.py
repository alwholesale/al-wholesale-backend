from django.db import models
from django.conf import settings
from products.models import Product

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart - {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered','Delivered' ),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="5% UAE VAT")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    shipping_address = models.TextField()
    billing_address = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='Bank Transfer')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    PAYOUT_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 🚀 NEW: Financial Ledger Fields
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    vendor_earning = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payout_status = models.CharField(max_length=20, choices=PAYOUT_CHOICES, default='pending')

    def __str__(self):
        product_name = self.product.name if self.product else 'Deleted Product'
        return f"#{self.order.id} - {self.quantity} x {product_name}"

# 🚀 NEW: Dispute/Ticketing Engine
class DisputeTicket(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='disputes')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='filed_disputes')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=(('open', 'Open'), ('resolved', 'Resolved'), ('refunded', 'Refunded')), default='open')
    created_at = models.DateTimeField(auto_now_add=True)