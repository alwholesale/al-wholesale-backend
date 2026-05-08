from rest_framework import generics, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from .serializers import CategorySerializer, ProductSerializer
from .models import Product, Category, ProductImage

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['unit_price', 'created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Product.objects.all().select_related('vendor', 'category')
        
        categories = self.request.query_params.getlist('category')
        if categories:
            qs = qs.filter(category__id__in=categories)
            
        vendor_id = self.request.query_params.get('vendor')
        if vendor_id:
            qs = qs.filter(vendor__id=vendor_id)
            
        price_min = self.request.query_params.get('unit_price__gte')
        price_max = self.request.query_params.get('unit_price__lte')
        if price_min:
            qs = qs.filter(unit_price__gte=price_min)
        if price_max:
            qs = qs.filter(unit_price__lte=price_max)
            
        if self.request.query_params.get('stock__gt'):
            qs = qs.filter(stock__gt=0)
            
        return qs

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        product = serializer.save(vendor=self.request.user)
        images_data = self.request.FILES.getlist('uploaded_images')
        
        for index, image_file in enumerate(images_data):
            if index == 0 and not product.image:
                product.image = image_file
                product.save()
            ProductImage.objects.create(product=product, image=image_file)

class MyProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user).order_by('-created_at')

class ProductDeleteView(generics.DestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user)

class ProductUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]



    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user)

    def perform_update(self, serializer):
        product = serializer.save(vendor=self.request.user)
        images_data = self.request.FILES.getlist('uploaded_images')
        if images_data :
            product.images.all().delete()
            
            product.image = images_data[0]
            product.save()
            
        for image_file in images_data:
            ProductImage.objects.create(product=product, image=image_file)