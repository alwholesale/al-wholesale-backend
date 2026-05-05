from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    # ── VENDOR SPECIFIC FIELDS (IMAGE STYLE) ──
    business_name = models.CharField(max_length=255, blank=True, null=True)
    tax_info = models.CharField(max_length=50, blank=True, null=True, verbose_name="VAT Number")
    country = models.CharField(max_length=100, default="United Arab Emirates")
    state = models.CharField(max_length=100, blank=True, null=True)
    
    # File upload field for VAT/License
    vat_license_file = models.FileField(upload_to='vendor_docs/', blank=True, null=True)
    
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"