from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from .serializers import RegisterSerializer, UserSerializer
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import IsApprovedVendor


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role  # JWT payload mein bhi rakho
        return token

    def validate(self, attrs):
        data = super().validate(attrs)  # access + refresh aata hai

        # YEH LINES RESPONSE BODY MEIN ROLE BHEJTI HAIN
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
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class VendorDashboardStatsView(APIView):
    permission_classes = [IsAuthenticated, IsApprovedVendor]

    def get(self, request):
        return Response({"message": "welcome to approved Dashboard"})