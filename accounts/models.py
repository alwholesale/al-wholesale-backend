from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Role Selection Logic
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True, null=True)

    # Vendor Specific Fields (Jo sirf Sellers ke liye honge)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    tax_info = models.CharField(max_length=50, blank=True, null=True, verbose_name="TRN Number")
    is_approved = models.BooleanField(default=False) # Admin verification ke liye

    def __str__(self):
        return f"{self.username} ({self.role})"