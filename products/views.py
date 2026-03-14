from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import CategorySerializer, ProductSerializer
from accounts.permissions import IsApprovedVendor
from .models import Product, Category
# Create your views here.

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    
class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsApprovedVendor]
    
    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)
              
    
class MyProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user).order_by('created_at')
    
class ProductDeleteView(generics.DestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user)
    
    
    