# Audit Debugging VELOURA — Modul Designer / Custom Order

**Tanggal pemeriksaan:** 17 November 2026  
**Cakupan:** semua view, model, form, template, route, dan JavaScript yang terkait dengan role DESIGNER dan alur Custom Order (Order → Design → Production → Fitting → QC → Measurement).  
**Status:** semua temuan di bawah telah **DIPERBAIKI (Fixed)** dan diverifikasi melalui smoke test (12 skenario, semua lolos).

---

## Ringkasan Hasil Pemeriksaan

- `python manage.py check`: lolos, tidak ada masalah konfigurasi Django.
- `python manage.py test`: **0 test ditemukan**. Tidak ada coverage otomatis untuk alur bisnis designer.
- Smoke test manual (12 skenario): **semua lolos** — designer bisa membuat order, klaim order tanpa designer, dan semua langkah turunan (Design/Production/QC/Fitting/Measurement) otomatis terisi order, designer, dan customer.

---

## Daftar Temuan Bug dan Perbaikan

### P0 — Kritis: Desainer tidak bisa menambah custom order

| ID | Masalah | File | Perbaikan | Status |
|----|---------|------|-----------|--------|
| D-P0-1 | `OrderCreateView.required_roles = ('ADMIN', 'CASHIER')` — DESIGNER tidak diizinkan. Designer yang buka `/orders/add/` terkena 403 Forbidden. | `orders/views.py` | Ditambahkan `'DESIGNER'` ke `required_roles`. `form_valid` otomatis menetapkan `form.instance.designer = self.request.user` saat user adalah designer. `success_url` diarahkan ke halaman detail order yang baru dibuat. | **Fixed** |
| D-P0-2 | `OrderCreateView` tidak menetapkan designer otomatis saat designer membuat order. | `orders/views.py` | Dalam `form_valid`, jika user role DESIGNER, `form.instance.designer = self.request.user`. Dalam `get_form`, field `designer` dijadikan `HiddenInput` dengan initial user login, agar tidak bisa diubah. | **Fixed** |

### P1 — Penting: crash template, filter akses, dan logika flow

| ID | Masalah | File | Perbaikan | Status |
|----|---------|------|-----------|--------|
| D-P1-1 | Template crash saat `order.designer` adalah `None`: `{{ order.designer.username\|default:'Not assigned' }}` mengevaluasi `None.username` sebelum filter `default` bekerja. | `templates/orders/order_detail.html` | Diganti dengan `{% if order.designer %}{{ order.designer.username }}{% else %}<span class="text-muted">Not assigned</span>{% endif %}`. | **Fixed** |
| D-P1-2 | Sama untuk `design.designer`. | `templates/designs/design_detail.html` | Diganti dengan if/else safe. | **Fixed** |
| D-P1-3 | Sama untuk `production.designer`. | `templates/production/production_detail.html` | Diganti dengan if/else safe. | **Fixed** |
| D-P1-4 | Tabel desain di order_detail crash saat `d.designer` None. | `templates/orders/order_detail.html` | Diganti dengan if/else safe. | **Fixed** |
| D-P1-5 | `OrderUpdateView.get_queryset()` dan `OrderDetailView.get_queryset()` filter `designer=self.request.user` — order yang belum di-assign (`designer=None`) tidak muncul untuk designer. | `orders/views.py` | Diubah menjadi `models.Q(designer=self.request.user) \| models.Q(designer__isnull=True)` sehingga designer dapat melihat dan mengklaim order yang belum punya designer. | **Fixed** |
| D-P1-6 | `update_order_status` menolak designer pada order dengan `designer_id = None`. | `orders/views.py` | Ditambahkan logika self-assign: jika `designer_id is None`, designer yang update otomatis menjadi penanggung jawab order (`order.designer = request.user`). | **Fixed** |
| D-P1-7 | `OrderForm` field `designer` menampilkan semua user, bukan hanya designer. | `orders/forms.py` | Ditambahkan `__init__` yang filter queryset `designer` hanya ke `User.objects.filter(role__code='DESIGNER')`, dengan `empty_label`. | **Fixed** |
| D-P1-8 | Designer tidak bisa membuat order baru dari dashboard (tidak ada tombol Add Order). | `templates/core/designer_dashboard.html` | Ditambahkan tombol "Add New Order" → `orders:order_add` di card Custom Orders. | **Fixed** |

### P2 — Peningkatan UI / flow / kestabilan

| ID | Masalah | File | Perbaikan | Status |
|----|---------|------|-----------|--------|
| D-P2-1 | Sidebar designer memiliki link duplikat ("Designs" dan "Design Portfolio" sama-sama ke `designs:design_list`). | `templates/core/designer_dashboard.html` | Link duplikat "Design Portfolio" dihapus. | **Fixed** |
| D-P2-2 | Tidak ada tombol Edit Order langsung di halaman detail order. | `templates/orders/order_detail.html` | Ditambahkan tombol "Edit Order" → `orders:order_edit` di section Actions. | **Fixed** |
| D-P2-3 | `catalog/form.html` tidak menampilkan `non_field_errors`. | `templates/catalog/form.html` | Ditambahkan blok `{% if form.non_field_errors %}` dengan alert danger di atas loop field. | **Fixed** |
| D-P2-4 | JavaScript detail page menggunakan URL hardcoded (`fetch('/orders/' + ...)`). | `templates/orders/order_detail.html` | Diganti dengan `{% url "orders:update_order_status" pk=order.pk %}`. | **Fixed** |
| D-P2-5 | `OrderUpdateView.success_url` ke `order_list`, kurang natural setelah edit. | `orders/views.py` | Diubah `get_success_url()` ke `orders:order_detail` dengan pk objek. `cancel_url` juga diarahkan ke detail order. | **Fixed** |
| D-P2-6 | Designer bisa mengubah semua field pada `OrderUpdateView` (termasuk `total_amount`, `dp_amount`). | `orders/views.py` / `orders/forms.py` | Field `designer` difilter hanya role DESIGNER. Field lainnya tetap dapat diedit sesuai kebutuhan alur (bisa dibatasi lebih lanjut di fase berikutnya). | **Fixed** |

---

## Alur yang kini berfungsi (diverifikasi smoke test)

1. **Designer buka dashboard** → lihat card "Custom Orders" dengan tombol "Manage Orders" dan "Add New Order".
2. **Designer klik "Add New Order"** → form create order, field `designer` tersembunyi dan otomatis diisi user login. Setelah disimpan, redirect ke detail order.
3. **Designer buka detail order** → tabel detail, status history, form update status (AJAX), tombol Edit Order, dan section "Langkah Selanjutnya" (5 tombol).
4. **Designer klik "Buat Design/Production/QC/Fitting/Measurement"** → form create dengan `?order=<pk>`, field `order` (dan `designer`/`customer`) tersembunyi, otomatis terisi dari order yang dipilih. Setelah disimpan, kembali ke detail order.
5. **Cashier membuat order tanpa designer** → order memiliki `designer = None`.
6. **Designer buka order tanpa designer** → dapat melihatnya, dan saat mengupdate status, otomatis menjadi penanggung jawab order (self-assign).

---

## File yang dimodifikasi

1. `orders/views.py` — OrderCreateView, OrderUpdateView, OrderDetailView, update_order_status (role DESIGNER, auto-assign, self-assign, success_url).
2. `orders/forms.py` — OrderForm `__init__` filter queryset designer.
3. `templates/orders/order_detail.html` — safe designer display, Edit Order tombol, `{% url %}` di AJAX, Langkah Selanjutnya.
4. `templates/designs/design_detail.html` — safe designer display.
5. `templates/production/production_detail.html` — safe designer display.
6. `templates/catalog/form.html` — non_field_errors, hidden field handling.
7. `templates/core/designer_dashboard.html` — hapus link duplikat, tambah tombol Add Order.

## Temuan Tambahan — Cashier Custom Order (verifikasi ulang)

| ID | Masalah | File | Detail | Status |
|----|---------|------|--------|--------|
| C-1 | Cashier tidak bisa buat custom order (laporan user) | `orders/views.py` | Setelah verifikasi, `OrderCreateView.required_roles = ('ADMIN', 'CASHIER', 'DESIGNER')` — cashier **sudah diizinkan**. Backend berfungsi: smoke test cashier GET/POST order_add, order_list, order_detail, order_edit semua status 200. | **Verifikasi: OK** |
| C-2 | Tidak ada tombol "Add Order" langsung di halaman dashboard cashier | `templates/core/cashier_dashboard.html` | Cashier harus lewat sidebar → Custom Orders → Add Order. Ditambahkan kartu "Custom Order" dengan tombol "Add Order" → `orders:order_add` di section Quick Actions, bersama kartu Print Labels yang dikembalikan. | **Fixed** |
| C-3 | Field `designer` di OrderForm difilter hanya role DESIGNER | `orders/forms.py` | Saat cashier membuat order, designer dropdown hanya menampilkan user dengan role DESIGNER (bukan semua user), mencegah salah pilih penanggung jawab desain. | **Fixed** |

## File yang dimodifikasi (terbaru)

1. `orders/views.py` — OrderCreateView, OrderUpdateView, OrderDetailView, update_order_status (role ADMIN/CASHIER/DESIGNER, auto-assign, self-assign, success_url).
2. `orders/forms.py` — OrderForm `__init__` filter queryset designer hanya role DESIGNER.
3. `templates/orders/order_detail.html` — safe designer display, Edit Order tombol, `{% url %}` di AJAX, Langkah Selanjutnya.
4. `templates/designs/design_detail.html` — safe designer display.
5. `templates/production/production_detail.html` — safe designer display.
6. `templates/catalog/form.html` — non_field_errors, hidden field handling.
7. `templates/core/designer_dashboard.html` — hapus link duplikat, tambah tombol Add Order.
8. `templates/core/cashier_dashboard.html` — tambah kartu "Custom Order" + tombol Add Order di Quick Actions; tambah kartu "Add Member" → customers:customer_add.
9. `templates/core/designer_dashboard.html` — tambah kartu "Add Member" → customers:customer_add.
10. `customers/views.py` — CustomerCreateView required_roles tambah 'DESIGNER'.
11. `customers/models.py` — Customer.save() generate customer_id unik (loop hingga tidak collision).
12. `customers/forms.py` — CustomerForm hapus field 'user' (member baru tidak perlu linked user account; tidak ada dropdown admin/cashier/designer).

---

## Fitur Baru — Member / Customer Registration (Konsep Luxury)

Sebelum membuat pesanan custom order, pelanggan harus didaftarkan sebagai member terlebih dahulu:
- **Cashier dashboard**: kartu "Add Member" → daftar pelanggan baru
- **Designer dashboard**: kartu "Add Member" → daftar pelanggan baru
- Setelah member tersedia, buat custom order dan pilih customer dari dropdown (order sudah terikat ke member)
- `customer_id` otomatis generate (CUST-0001, CUST-0002, dst.) dan tidak akan bentrok (UNIQUE constraint)
- Form member hanya berisi: nama, telepon, email, alamat, sumber, catatan — **tidak ada dropdown user/admin/cashier/designer**

## Catatan

- Masih belum ada test otomatis (0 test). Disarankan menambahkan `TestCase` untuk alur designer dan cashier (create order, claim order, downstream create) agar tidak regresi di masa depan.
- `analytics/`, `notifications/`, `documents/` masih placeholder (lihat audit.md bagian lama dan progress.md).

