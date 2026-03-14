from django.urls import path
from .views import *
urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="categories-list"),
    path("create/", ProductCreateView.as_view(), name="product-create"),
    path('my-products/', MyProductListView.as_view(), name='my-products'),      
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
]
