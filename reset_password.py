"""
Reset admin password from environment variables.
Safe to run - only changes password, never deletes users or data.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ojt_tracker.settings')
django.setup()

from django.contrib.auth.models import User

username = os.environ.get('RESET_USERNAME', '')
new_password = os.environ.get('RESET_PASSWORD', '')

if not username or not new_password:
    print("⚠️  RESET_USERNAME or RESET_PASSWORD not set. Skipping.")
else:
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        print(f"✅ Password for '{username}' has been reset successfully.")
        print(f"ℹ️  Total users in database: {User.objects.count()}")
        print("ℹ️  All usernames:")
        for u in User.objects.all():
            print(f"   - {u.username} | staff: {u.is_staff} | superuser: {u.is_superuser}")
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found.")
        print("ℹ️  Available usernames:")
        for u in User.objects.all():
            print(f"   - {u.username}")
