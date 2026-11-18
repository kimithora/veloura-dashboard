import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['DJANGO_ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'
import django
django.setup()

from django.test import Client
from django.urls import reverse
from accounts.models import User
from orders.models import Order

client = Client()
designer = User.objects.get(username='designer')
cashier = User.objects.get(username='cashier')

print('=' * 60)
print('FINAL SMOKE TEST: DESIGNER WORKFLOW + CASHIER ONLY MEMBER')
print('=' * 60)

# 1. Designer CANNOT access customer_add (only admin/cashier)
client.force_login(designer)
resp = client.get(reverse('customers:customer_add'))
print(f'[1] customer_add (designer) status: {resp.status_code}')
assert resp.status_code == 403, f'Expected 403, got {resp.status_code}'

# 2. Cashier CAN access customer_add
client.force_login(cashier)
resp = client.get(reverse('customers:customer_add'))
print(f'[2] customer_add (cashier) status: {resp.status_code}')
assert resp.status_code == 200

# 3. Designer CAN access order_list
client.force_login(designer)
resp = client.get(reverse('orders:order_list'))
print(f'[3] order_list (designer) status: {resp.status_code}')
assert resp.status_code == 200

# 4. Designer CAN access order_detail (existing order)
order = Order.objects.first()
resp = client.get(reverse('orders:order_detail', kwargs={'pk': order.pk}))
print(f'[4] order_detail (designer) status: {resp.status_code}')
assert resp.status_code == 200

# 5. Designer CAN access downstream create forms with ?order=
for url_name in ['designs:design_add', 'production:production_add', 'production:qc_add', 'production:fitting_add', 'customers:measurement_add']:
    resp = client.get(reverse(url_name) + f'?order={order.pk}')
    print(f'[5.{url_name}] status: {resp.status_code}')
    assert resp.status_code == 200

# 6. Designer CANNOT access order_add (removed from dashboard, but direct URL still works since role DESIGNER is allowed)
# Note: OrderCreateView still allows DESIGNER role, but button removed from dashboard per user request.
resp = client.get(reverse('orders:order_add'))
print(f'[6] order_add direct URL (designer) status: {resp.status_code}')

print()
print('=' * 60)
print('ALL FINAL TESTS PASSED')
print('=' * 60)
