import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['DJANGO_ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'
import django
django.setup()

from django.test import Client
from django.urls import reverse
from accounts.models import User
from customers.models import Customer

client = Client()
cashier = User.objects.get(username='cashier')
designer = User.objects.get(username='designer')

print('=' * 60)
print('SMOKE TEST: CUSTOMER / MEMBER REGISTRATION')
print('=' * 60)

# Cashier can access customer_add
client.force_login(cashier)
resp = client.get(reverse('customers:customer_add'))
print(f'[1] customer_add (cashier) GET status: {resp.status_code}')
assert resp.status_code == 200

# Cashier creates customer
resp = client.post(reverse('customers:customer_add'), {
    'full_name': 'Luxury Client Smoke',
    'phone': '+628123456789',
    'email': 'luxury@example.com',
    'address': 'Jl. Mawar No. 1, Jakarta',
    'source': 'WALK_IN',
    'notes': 'VIP member smoke test',
}, follow=True)
print(f'[2] customer_add (cashier) POST status: {resp.status_code}')
assert resp.status_code == 200
cust = Customer.objects.filter(full_name='Luxury Client Smoke').first()
assert cust is not None, 'Customer not created'
print(f'    -> Customer created: {cust.customer_id} - {cust.full_name}')
cust.delete()

# Designer can access customer_add
client.force_login(designer)
resp = client.get(reverse('customers:customer_add'))
print(f'[3] customer_add (designer) GET status: {resp.status_code}')
assert resp.status_code == 200

# Designer creates customer
resp = client.post(reverse('customers:customer_add'), {
    'full_name': 'Designer Client Smoke',
    'phone': '+628123456788',
    'email': 'designer@example.com',
    'address': 'Jl. Melati No. 2, Jakarta',
    'source': 'REFERRAL',
    'notes': 'Designer member smoke test',
}, follow=True)
print(f'[4] customer_add (designer) POST status: {resp.status_code}')
assert resp.status_code == 200
cust2 = Customer.objects.filter(full_name='Designer Client Smoke').first()
assert cust2 is not None, 'Customer not created by designer'
print(f'    -> Customer created: {cust2.customer_id} - {cust2.full_name}')
cust2.delete()

# Customer list accessible by both
client.force_login(cashier)
resp = client.get(reverse('customers:customer_list'))
print(f'[5] customer_list (cashier) status: {resp.status_code}')
assert resp.status_code == 200

client.force_login(designer)
resp = client.get(reverse('customers:customer_list'))
print(f'[6] customer_list (designer) status: {resp.status_code}')
assert resp.status_code == 200

print()
print('=' * 60)
print('ALL CUSTOMER/MEMBER TESTS PASSED')
print('=' * 60)
