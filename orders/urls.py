from django.urls import path
from .views import (
    CartAPIView, CheckoutAPIView, VendorOrderListAPIView, 
    VendorOrderStatusUpdateAPIView, BuyerOrderListAPIView, CartSyncAPIView,
    AdminAllOrdersView, AdminPayoutsView
)

urlpatterns = [
    # Cart & Checkout
    path('cart/', CartAPIView.as_view(), name='cart-api'),
    path('cart/sync/', CartSyncAPIView.as_view(), name='cart-sync'),
    path("checkout/", CheckoutAPIView.as_view(), name="checkout"),
    
    # Vendor Orders
    path('vendor-orders/', VendorOrderListAPIView.as_view(), name='vendor-orders'),
    path('vendor-orders/<int:pk>/update/', VendorOrderStatusUpdateAPIView.as_view(), name='vendor-order-update'),
    
    # Buyer Orders
    path('my-orders/', BuyerOrderListAPIView.as_view(), name='my-orders'),
    
    # 🚀 NEW: Master Admin Orders & Payout Routes
    path('admin/all/', AdminAllOrdersView.as_view(), name='admin-all-orders'),
    path('admin/payouts/', AdminPayoutsView.as_view(), name='admin-payouts'),
    path('admin/payouts/<int:pk>/', AdminPayoutsView.as_view(), name='admin-payout-update'),
]