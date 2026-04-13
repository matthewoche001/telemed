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
from admin_panel.models import AuditLog

def final_system_check():
    client = Client()
    print("--- FULL SYSTEM INTEGRATION CHECK ---")

    # Setup Admin
    admin_user, _ = User.objects.get_or_create(username='test_admin', defaults={'role': 'admin'})
    admin_user.set_password('admin123')
    admin_user.save()
    
    # 1. Test Admin Dashboard
    client.login(username='test_admin', password='admin123')
    urls = [
        'admin_panel:dashboard',
        'admin_panel:staff_list',
        'admin_panel:inventory_list',
        'admin_panel:audit_logs',
        'notifications:list',
        'diagnostics:history',
    ]
    
    for url_name in urls:
        response = client.get(reverse(url_name))
        if response.status_code == 200:
            print(f"SUCCESS: {url_name} reachable (200)")
        else:
            print(f"FAILED: {url_name} returned {response.status_code}")

    # 2. Test CSV Export
    response = client.get(reverse('admin_panel:export_audit_csv'))
    if response.status_code == 200 and response['Content-Type'] == 'text/csv':
        print("SUCCESS: Audit Log CSV Export is functional")
    else:
        print("FAILED: CSV Export failed")

    # 3. Test Role Redirects
    client.logout()
    response = client.get('/', follow=True)
    if 'accounts/login' in response.redirect_chain[0][0]:
        print("SUCCESS: Root redirect to login (Unauthenticated) works")

    print("\n--- SYSTEM CHECK COMPLETE ---")

if __name__ == "__main__":
    final_system_check()
