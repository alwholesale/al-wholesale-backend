from django.urls import path
from .views import (
    CategoryListView,
    ProductListView,
    ProductCreateView,
    ProductDetailView,
    MyProductListView,
    ProductDeleteView,
    ProductUpdateView,
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='categories-list'),
    path('', ProductListView.as_view(), name='product-list'),                    # GET /api/products/
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('my-products/', MyProductListView.as_view(), name='my-products'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),       # GET /api/products/1/
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'), # PATCH /api/products/1/update/
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'), # DELETE /api/products/1/delete/
]