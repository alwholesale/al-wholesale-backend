from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from .serializers import CategorySerializer, ProductSerializer
from .models import Product, Category, ProductImage


# ==========================================
# 🚀 SECURITY: MASTER ADMIN PERMISSION
# ==========================================
class IsMasterAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin'))


# ==========================================
# 🏷️ CATEGORY MANAGEMENT
# ==========================================
class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsMasterAdmin()]
        return [permissions.AllowAny()]


class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsMasterAdmin]


# ==========================================
# 🛍️ PUBLIC PRODUCT LIST (SHOP PAGE)
# ==========================================
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    
    search_fields = ['name', 'description'] 
    ordering_fields = ['unit_price', 'created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        # Only show Approved AND Active products
        qs = Product.objects.filter(is_approved=True, is_active=True).select_related('vendor', 'category').prefetch_related('images')
        
        # Category filter
        categories = self.request.query_params.getlist('category')
        if categories:
            qs = qs.filter(category__id__in=categories)
        
        # Vendor filter
        vendor_id = self.request.query_params.get('vendor')
        if vendor_id:
            qs = qs.filter(vendor__id=vendor_id)
        
        # Price range filter
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        if price_min:
            qs = qs.filter(unit_price__gte=price_min)
        if price_max:
            qs = qs.filter(unit_price__lte=price_max)
        
        # Stock filter
        if self.request.query_params.get('in_stock') == 'true':
            qs = qs.filter(stock__gt=0)
            
        return qs


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_approved=True, is_active=True).select_related('vendor', 'category').prefetch_related('images')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


# ==========================================
# 🏪 VENDOR PRODUCT MANAGEMENT
# ==========================================
class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # New product: pending approval but active
        product = serializer.save(vendor=self.request.user, is_approved=False, is_active=True)
        
        # Handle multiple images
        images_data = self.request.FILES.getlist('uploaded_images')
        for index, image_file in enumerate(images_data):
            if index == 0 and not product.image:
                product.image = image_file
                product.save(update_fields=['image'])
            ProductImage.objects.create(product=product, image=image_file)


class MyProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user).prefetch_related('images').order_by('-created_at')


class ProductDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user)


class ProductUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user)

    def perform_update(self, serializer):
        # When edited, product goes back to pending approval
        product = serializer.save(vendor=self.request.user, is_approved=False, is_active=True)
        
        # Handle image updates
        images_data = self.request.FILES.getlist('uploaded_images')
        if images_data:
            # Clear existing images
            product.images.all().delete()
            # Set first image as main
            product.image = images_data[0]
            product.save(update_fields=['image'])
            # Create all images
            for image_file in images_data:
                ProductImage.objects.create(product=product, image=image_file)


# ==========================================
# ⚖️ MASTER ADMIN MODERATION ENGINE
# ==========================================
class AdminProductModerationView(APIView):
    permission_classes = [IsMasterAdmin] 

    def get(self, request):
        # Show all pending products
        products = Product.objects.filter(is_approved=False).select_related('vendor').prefetch_related('images').order_by('-created_at')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            product = Product.objects.get(id=pk)
            action = request.data.get('action')
            
            if action == 'approve':
                product.is_approved = True
                product.is_active = True 
                product.save()
                return Response({"message": "Product Approved & Activated Successfully!"})
            
            elif action == 'reject':
                product.delete()
                return Response({"message": "Product Rejected and Deleted."})
            
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
            
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)