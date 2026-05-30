from rest_framework import serializers
from .models import SiteSetting, HomePageBanner

class SiteSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSetting
        fields = '__all__'
        
        
class HomePageBannerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = HomePageBanner
        fields = '__all__'
        