from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminSiteSettingAPIView, PublicCMSDataAPIView, AdminBannerViewSet


router = DefaultRouter()
router.register(r'admin/banners', AdminBannerViewSet, basename='admin-banner')

urlpatterns = [
    # Customer Hit Karega
    path('public/data/', PublicCMSDataAPIView.as_view(), name='public-cms-data'),
    
    # Admin Panel Hit Karega
    path('admin/settings/', AdminSiteSettingAPIView.as_view(), name='admin-settings'),
    
    # Banners ke saare routes (GET, POST, PATCH, DELETE) automatically ban jayenge
    path('', include(router.urls)), 
]