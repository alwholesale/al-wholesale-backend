from django.urls import path
from .views import (
    CategoryListCreateAPIView, CategoryDetailAPIView,
    ProductListView, ProductCreateView, ProductDetailView,
    MyProductListView, ProductDeleteView, ProductUpdateView,
    AdminProductModerationView
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListCreateAPIView.as_view(), name='categories-list'),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='category-detail'),
    
    # Public & Vendor Products
    path('', ProductListView.as_view(), name='product-list'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('my-products/', MyProductListView.as_view(), name='my-products'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product-detail-update'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    
    # 🚀 NEW: Master Admin Moderation Routes
    path('admin/moderate/', AdminProductModerationView.as_view(), name='admin-moderate-products'),
    path('admin/moderate/<int:pk>/', AdminProductModerationView.as_view(), name='admin-moderate-product-action'),
]