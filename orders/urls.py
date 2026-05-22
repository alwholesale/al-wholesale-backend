from django.urls import path
from .views import CartAPIView, CheckoutAPIView, VendorOrderListAPIView, VendorOrderStatusUpdateAPIView, BuyerOrderListAPIView, CartSyncAPIView


urlpatterns = [
     path('cart/', CartAPIView.as_view(), name='cart-api'),
     path('cart/sync/', CartSyncAPIView.as_view(), name='cart-sync'), # 🚀 Yeh nayi route add karni hai
     path("checkout/", CheckoutAPIView.as_view(), name="checkout"),
     path('vendor-orders/', VendorOrderListAPIView.as_view(), name='vendor-orders'),
     path('vendor-orders/<int:pk>/update/', VendorOrderStatusUpdateAPIView.as_view(), name='vendor-order-update'),
     path('my-orders/', BuyerOrderListAPIView.as_view(), name='my-orders'),
     ]
