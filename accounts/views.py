from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.exceptions import AuthenticationFailed  # 🚀 NEW: Security Error
from .models import User
from .serializers import RegisterSerializer, UserProfileSerializer, AdminVendorSerializer, AdminUserSerializer
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model

User = get_user_model()

# 🚀 Custom Master Admin Permission
class IsMasterAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin'))

# ================= AUTHENTICATION & LOGIN =================
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role  
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # 🚨 ELITE SECURITY FIX: Block unapproved vendors from logging in!
        if self.user.role == 'vendor' and not self.user.is_approved:
            raise AuthenticationFailed("Account Pending Approval: Your vendor account is currently under review by the Administration. You cannot login yet.")

        data['role'] = self.user.role
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['business_name'] = self.user.business_name or ''
        data['is_approved'] = self.user.is_approved
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

# ================= USER PROFILE =================
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


# ================= MASTER ADMIN MODULES =================
class AdminAllVendorsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsMasterAdmin] 

    def get(self, request):
        vendors = User.objects.filter(role='vendor').order_by('-date_joined')
        serializer = AdminVendorSerializer(vendors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AdminAllUsersView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsMasterAdmin] 

    def get(self, request):
        users = User.objects.filter(role='customer').order_by('-date_joined')
        serializer = AdminUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class VendorApproveAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsMasterAdmin] 

    def patch(self, request, pk):
        try:
            vendor = User.objects.get(id=pk, role='vendor')
            action = request.data.get('action') 

            if action == 'approve':
                vendor.is_approved = True
                vendor.save()
                return Response({"message": f"Vendor {vendor.business_name} has been approved successfully!"}, status=status.HTTP_200_OK)
            
            elif action == 'reject':
                vendor.delete()
                return Response({"message": "Vendor application rejected and removed."}, status=status.HTTP_200_OK)
            
            elif action == 'suspend':
                vendor.is_approved = False
                vendor.save()
                return Response({"message": f"Vendor {vendor.business_name} suspended."}, status=status.HTTP_200_OK)
            
            return Response({"error": "Invalid action. Use 'approve', 'reject' or 'suspend'."}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"error": "Vendor not found."}, status=status.HTTP_404_NOT_FOUND)