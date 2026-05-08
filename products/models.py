from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', blank=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    
    # Pricing Logic
    unit_price = models.DecimalField(max_digits=10, decimal_places=2) 
    bulk_price = models.DecimalField(max_digits=10, decimal_places=2) 
    min_order_quantity = models.IntegerField(default=10)
    
    stock = models.IntegerField(default=0)
    unit = models.CharField(max_length=50, help_text="e.g., kg, carton, bag") 
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.vendor.business_name if self.vendor.business_name else self.vendor.username}"

# Multiple Images ke liye naya model
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    
    def __str__(self):
        return f"Image for {self.product.name}"