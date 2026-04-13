import os
import django
from django.test import Client
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ohms.settings')
django.setup()

from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from accounts.models import User

def check_all():
    client = Client()
    print("--- Final System Verification ---")
    
    admin, _ = User.objects.get_or_create(username='verifier', defaults={'role': 'admin'})
    admin.set_password('pass123')
    admin.save()
    
    client.login(username='verifier', password='pass123')
    
    urls = [
        'admin_panel:dashboard',
        'admin_panel:staff_list',
        'admin_panel:inventory_list',
        'admin_panel:audit_logs',
        'diagnostics:history',
        'notifications:list',
    ]
    
    success = True
    for u in urls:
        resp = client.get(reverse(u))
        if resp.status_code == 200:
            print(f"OK: {u}")
        else:
            print(f"FAIL: {u} -> {resp.status_code}")
            success = False
            
    if success:
        print("\nSUCCESS: All administrative and global UI modules are verified.")

if __name__ == "__main__":
    check_all()
