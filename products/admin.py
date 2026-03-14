from django.contrib import admin
from django.db import models
from django.contrib.auth.admin import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'unit_price', 'stock', 'created_at']
    list_filter = ['category', 'vendor']
    search_fields = ['name', 'description']
        
    
