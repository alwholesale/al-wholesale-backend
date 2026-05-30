from django.db import models

# 1. THE GLOBAL VARIABLES (Singleton Pattern)
class SiteSetting(models.Model):
    platform_name = models.CharField(max_length=255, default="Al Wholesale")
    support_email = models.EmailField(default="support@alwholesale.ae")
    support_phone = models.CharField(max_length=20, default="+971 00 000 0000")
    default_vat_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    platform_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    maintenance_mode = models.BooleanField(default=False)
    
    # 🚀 NEW: Infinite Marquee Text
    marquee_text = models.CharField(max_length=500, blank=True, null=True, help_text="Scrolling text for top banner")

    def save(self, *args, **kwargs):
        self.pk = 1 # Yeh make sure karega ki settings ki sirf 1 hi row ho database mein
        super(SiteSetting, self).save(*args, **kwargs)
        
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
        
    def __str__(self):
        return f"{self.platform_name} - Global Settings"

# 2. DYNAMIC HOMEPAGE BANNERS
class HomePageBanner(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='cms/banners/')
    redirect_url = models.CharField(max_length=255, blank=True, null=True, help_text="e.g. /shop?category=2")
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0, help_text="Lowest number shows first")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title