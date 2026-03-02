"""
Auto-create superuser from environment variables during deployment.
Run via build command on Render.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ojt_tracker.settings')
django.setup()

from django.contrib.auth.models import User

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@ojt.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')

if not password:
    print("⚠️  DJANGO_SUPERUSER_PASSWORD not set. Skipping superuser creation.")
else:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"✅ Superuser '{username}' created successfully.")
    else:
        print(f"ℹ️  Superuser '{username}' already exists. Skipping.")
