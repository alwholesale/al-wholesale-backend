import os
import django

# Django environment setup karne ke liye
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from products.models import Category

def seed():
    categories = ['Meat & Poultry', 'Grains & Rice', 'Dairy & Eggs', 'Oils & Fats', 'Beverages', 'Spices']
    for cat_name in categories:
        Category.objects.get_or_create(name=cat_name)
    print("Categories Seeded Successfully!")

if __name__ == '__main__':
    seed()