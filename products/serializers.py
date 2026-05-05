from rest_framework import serializers
from .models import Product, Category, ProductImage

# Naya serializer banayein images ke liye
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    vendor_name = serializers.ReadOnlyField(source='vendor.business_name')
    category_name = serializers.ReadOnlyField(source='category.name')
    # Product ki saari images yahan attach ho jayengi
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['vendor'] # Vendor backend se auto-assign hoga