import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings') # Apne project ka sahi naam likhein
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = 'admin_mueez' # Apni marzi ka username
email = 'mueezur@gmail.com'
password = 'Mueez_Admin#123@' # Apna password dalo

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created successfully!")
else:
    print(f"Superuser '{username}' already exists.")