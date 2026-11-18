# VELOURA — Fashion Management System

An integrated fashion business management system built with **Python Django** (Backend) and **HTML5/CSS3/JavaScript** (Frontend, Bootstrap 5). Designed for Windows local development with SQLite (architecture prepared for MariaDB/MySQL).

## Business Areas Covered
- Couture Services (custom orders)
- Own Products (Veloura originals)
- Third-Party Products (purchased & consignment)

## User Roles & Access Control
- **ADMIN** — full system access (users, products, inventory, suppliers, customers, analytics, reports)
- **CASHIER** — retail operations (POS, sales, customers, products, inventory, payments)
- **DESIGNER** — fashion design & production (designs, custom orders, measurements, production). Designer **cannot create customers** (ADMIN/CASHIER only) and sees no "Add" buttons on list pages — they continue custom order stages from the order detail page.

Role authorization is enforced **on the backend**, not only hidden in the frontend.

## Technology Stack
- Backend: Django 6.0.10 (Python 3.14)
- Database: SQLite (`db.sqlite3`) — `.env` variables prepare migration to MariaDB/MySQL
- UI: Bootstrap 5 + custom Veloura stylesheet
- Icons: Lucide
- Barcode: python-barcode + Pillow (Code 128)
- PDF: ReportLab

## Quick Start (Windows)

### 1. Prerequisites
```powershell
python --version   # Python 3.14
pip --version
```

### 2. Install dependencies
```powershell
pip install django pillow python-barcode reportlab
```

### 3. Apply migrations
```powershell
python manage.py migrate
```

### 4. Create roles and default users (one-time seed)
The system ships with no hardcoded permanent sample data, but for first-time local setup you can create roles and users:

```powershell
# Create roles
python manage.py shell << 'EOF'
from accounts.models import Role, User
for code, name in [('ADMIN','Admin'),('CASHIER','Cashier'),('DESIGNER','Designer')]:
    Role.objects.get_or_create(code=code, defaults={'name':name})
# Create users
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin','admin@veloura.com','admin123', role=Role.objects.get(code='ADMIN'), first_name='Veloura', last_name='Admin')
if not User.objects.filter(username='cashier').exists():
    User.objects.create_user('cashier','cashier@veloura.com','cashier123', role=Role.objects.get(code='CASHIER'), first_name='Sarah', last_name='Cashier')
if not User.objects.filter(username='designer').exists():
    User.objects.create_user('designer','designer@veloura.com','designer123', role=Role.objects.get(code='DESIGNER'), first_name='Elena', last_name='Designer')
EOF
```

Default credentials:
- `admin` / `admin123` (Admin)
- `cashier` / `cashier123` (Cashier)
- `designer` / `designer123` (Designer)

### 5. Run the development server
```powershell
python manage.py runserver 127.0.0.1:8000
```
Open http://127.0.0.1:8000/ and log in. You are redirected to your role's dashboard.

### 6. Django Admin
Users/roles can also be managed at http://127.0.0.1:8000/admin/ (superuser only).

## What Is Implemented (Working & Tested)

### Phase 1 — Foundation
- Django project, 14 modular apps, settings
- Custom user model + 3 roles with backend authorization
- Login / logout, session handling
- Role-based dashboards: Admin, Cashier, Designer
- Sidebar navigation, top bar, notifications area, profile dropdown
- SQLite database; `.env` variables (`DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) prepare migration to MariaDB/MySQL

### Phase 2 — Catalogue & Inventory
- Brands, Categories, Products (SKU, source: Veloura Original / Third-Party Purchased / Third-Party Consignment, supplier, prices, stock, image, status)
- Product Variants (size, color, unique barcode, stock)
- Barcode registry (Code 128, unique, admin-only regeneration)
- Customers (profile, purchase history link)
- Suppliers (direct purchase & consignment types)
- Materials (raw & supporting), stock adjustments
- **Stock movement ledger** (purchase, sales, production usage/output, return, adjustment, damage/loss) with previous/new stock, reference, user, timestamp

### Phase 3 — Point of Sale, Barcode & Transactions
- Barcode scanner API (camera/USB keyboard-emulation or manual input)
- Identifies product/variant; shows name, image, price, size, color, stock; validates active/available
- Session-based shopping cart (add, change quantity, remove, clear)
- Checkout creates a **PENDING / UNPAID** transaction (stock is NOT deducted yet) and can record the payment chosen in the POS modal
- Payment methods: Cash, Bank Transfer, QRIS; payment proof upload
- Payment confirmation → transaction **COMPLETED / PAID** → **stock deducted** only then
- `select_for_update()` row locking + stock availability check → prevents overselling
- Every stock change recorded in StockMovement ledger
- `stock_deducted` flag → prevents duplicate stock deduction on resubmission
- Cancelled transactions restore stock via RETURN movements; cancel button is wired from the UI
- Barcode label download in **PNG** and **PDF** (printable, with product name/SKU/barcode)

### Phase 4 — Payments & Invoices
- Payment records (pending/confirmed/failed/refunded), independently tracked from order status
- Partial payments supported (DP / installment); transaction marked PAID only when confirmed total covers grand total
- Void/refund recalculates transaction status and returns stock when the transaction is no longer covered
- Sales invoice PDF (Veloura branding, itemised table, totals)
- **Custom order payments** (`OrderPayment`): DP / installment / full payment on custom orders, with confirm/void, automatic `dp_amount` sync on the order, and a filterable list page at `/payments/orders/`

### Phase 5 — Custom Order, Design & Production (Implemented)
- Custom orders with status workflow (RECEIVED → … → DELIVERED), status history, and edit/claim logic
- Designer assignment: designer sees own **and unassigned** records and can claim them; records for other designers return 403
- Customer measurements (linked to order, with `?order=` preselect)
- Design management with version snapshots on each status update; approving a design advances the order status
- Production records with progress updates, material requests (approve/reject/fulfill → stock ledger), material usage (row-locked stock deduction)
- Fitting sessions and quality-control checklist (all items must pass before PASSED)
- "Next steps" panel on order detail: create Design / Production / QC / Fitting / Measurement with `?order=` preselect
- Customer Orders table (`/customers/orders/`) showing each customer's orders and production progress

### Marked "Coming Soon" (future phases)
- Business analytics (Chart.js), in-app notifications, additional PDF reports, sales reports
- `analytics/`, `notifications/`, `documents/` remain placeholder apps

## Project Structure
```
config/             Django project settings & URLs
accounts/           Users & roles
customers/          Customer management + measurements + customer-orders table
suppliers/          Supplier management (direct + consignment)
catalog/            Products, variants, barcodes, labels
inventory/          Materials & stock movement ledger
sales/              Transactions, POS, cart, invoice PDF
payments/           Payment records (POS) & custom-order payments (OrderPayment)
orders/             Custom orders, status history, next-steps panel
designs/            Design management with version snapshots
production/         Production, material requests/usage, fittings, QC
documents/          (placeholder — future phase)
analytics/          (placeholder — future phase)
notifications/      (placeholder — future phase)
core/               Base models, dashboards, middleware, context processors
static/             CSS, JS, Bootstrap, Lucide
templates/          Django templates
db.sqlite3          Local development database (see Notes)
ERD.md              Full entity-relationship documentation (schema)
relasi.md           Relation/cardinality summary
audit.md            Debugging & fix log
progress.md         Phase status overview
sistemflow.mmd      Detailed Mermaid flowchart of the whole system
sistemsimple.mmd    Simplified Mermaid flowchart
database_erd.mmd    Mermaid ERD diagram
```

## Database State (Demo Reset — 19 Nov 2026)
The database was **wiped for demo presentation**: all business data (customers, products, transactions, orders, designs, production, payments, stock ledger, sessions) was deleted. **Only users and roles remain:**

| Username | Role | Password |
|---|---|---|
| `admin` | ADMIN | `admin123` |
| `cashier` | CASHIER | `cashier123` |
| `designer` | DESIGNER | `designer123` |

A pre-wipe backup exists as `db_backup_20261119_035957.sqlite3` (untracked). Restore it by copying over `db.sqlite3` if the old data is needed.

## Database Migration to MariaDB/MySQL
Set environment variables and the engine will switch from SQLite:
```powershell
$env:DB_ENGINE='django.db.backends.mysql'
$env:DB_NAME='veloura'
$env:DB_USER='veloura'
$env:DB_PASSWORD='yourpassword'
$env:DB_HOST='localhost'
$env:DB_PORT='3306'
python manage.py migrate
```
(Install `mysqlclient` Python package for MySQL/MariaDB support.)

## Notes
- The shipped database contains only the three demo users/roles (see "Database State" above); all business records are created at runtime.
- Monetary values use Django `DecimalField` (never floats).
- Historical transactions are preserved when products/customers are archived.
- Automated test suite is currently empty (`manage.py test` → 0 tests); verification is done via manual smoke scripts (`run_member_smoke.py`, `run_final.py`).
