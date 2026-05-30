from django.shortcuts import render
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from .models import HomePageBanner, SiteSetting
from .serializers import SiteSettingSerializer, HomePageBannerSerializer

# 🚀 ELITE FIX: Custom Master Admin Permission
class IsMasterAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin'))

# PUBLIC APIS (For Customers Frontend)
class PublicCMSDataAPIView(APIView):
    permission_classes = [permissions.AllowAny] 
    
    def get(self, request):
        settings = SiteSetting.load()
        banners = HomePageBanner.objects.filter(is_active=True)
        return Response({
            "settings": SiteSettingSerializer(settings).data,
            "banners": HomePageBannerSerializer(banners, many=True).data
        }, status=status.HTTP_200_OK)

# super Admin API master Control
class AdminSiteSettingAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes  = [IsMasterAdmin] # 🚀 FIXED HERE
    
    def get(self, request):
        settings = SiteSetting.load()
        return Response(SiteSettingSerializer(settings).data)
        
    def patch(self, request):
        settings = SiteSetting.load()
        serializer = SiteSettingSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminBannerViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsMasterAdmin] # 🚀 FIXED HERE
    parser_classes = [MultiPartParser, FormParser] 
    queryset = HomePageBanner.objects.all()
    serializer_class = HomePageBannerSerializer