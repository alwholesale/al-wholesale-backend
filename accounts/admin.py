from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
# Register your models here.

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
    ('Business Info', {'fields': ('role', 'phone', 'business_name', 'tax_info', 'is_approved')}),
    )
    list_display = ['username', 'email', 'role', 'is_approved', 'is_staff']
    list_filter = ['role', 'is_approved']

admin.site.register(User, CustomUserAdmin)
