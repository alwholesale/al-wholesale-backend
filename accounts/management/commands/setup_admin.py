from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        # Admin Create Karein
        if not User.objects.filter(username='admin_mueez').exists():
            User.objects.create_superuser('admin_mueez', 'admin@example.com', 'Admin@12345')
            self.stdout.write("Superuser created!")
        
        # Seller ko Approve Karein
        seller = User.objects.filter(username='mueezurrehman').first()
        if seller:
            seller.is_active = True
            seller.save()
            self.stdout.write("Seller approved!")