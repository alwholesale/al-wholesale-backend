from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'phone', 'business_name', 'tax_info')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role', 'phone', 'business_name', 'tax_info', 'country', 'state', 'vat_license_file')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            role=validated_data.get('role', 'customer'),
            phone=validated_data.get('phone'),
            business_name=validated_data.get('business_name'),
            tax_info=validated_data.get('tax_info'),
            country=validated_data.get('country'),
            state=validated_data.get('state'),
            vat_license_file=validated_data.get('vat_license_file')
        )
        return user
    
    
# Niche ye add karo
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'business_name', 'tax_info')
        read_only_fields = ('username', 'email') # Email aur Username change nahi hone denge safety ke liye 