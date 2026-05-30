from rest_framework import serializers
from .models import Product, Category, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    # 🚀 ELITE FIX: Yeh API ko kabhi crash nahi hone dega!
    vendor_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['vendor'] 

    def get_vendor_name(self, obj):
        if obj.vendor:
            return obj.vendor.business_name or obj.vendor.username
        return "Unknown Vendor"

    def get_category_name(self, obj):
        # Agar admin ne category delete kar di hai, toh crash mat karo!
        if obj.category:
            return obj.category.name
        return "Uncategorized"