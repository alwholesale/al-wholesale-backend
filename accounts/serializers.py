from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'phone', 'business_name', 'tax_info', 'is_approved')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role', 'phone', 'business_name', 'tax_info', 'country', 'state', 'vat_license_file')

    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.pop('role', 'customer')
        
        # 🚀 SECURE FIX: Only allow customer or vendor via API
        if role not in ['customer', 'vendor']:
            role = 'customer'
        
        user = User.objects.create_user(
            password=password,
            role=role,
            **validated_data
        )
        return user 

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'business_name', 'tax_info', 'country', 'state')
        read_only_fields = ('username', 'email')

class AdminVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'business_name', 'tax_info', 'vat_license_file', 'is_approved', 'date_joined')

# ==========================================
# 🚀 ELITE FIX: THE MISSING ADMIN USER SERIALIZER
# ==========================================
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'country', 'state', 'date_joined', 'is_active')