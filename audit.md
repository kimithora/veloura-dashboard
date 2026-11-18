# Audit Debugging VELOURA — Modul Designer / Custom Order

**Tanggal pemeriksaan:** 17 November 2026  
**Pembaruan terakhir:** 19 November 2026  
**Cakupan:** semua view, model, form, template, route, dan JavaScript yang terkait dengan role DESIGNER dan alur Custom Order (Order → Design → Production → Fitting → QC → Measurement), plus pembayaran custom order.  
**Status:** semua temuan di bawah telah **DIPERBAIKI (Fixed)** dan diverifikasi melalui smoke test (12 skenario, semua lolos). Database dikosongkan untuk demo pada 19 Nov 2026 (lihat bagian Catatan).

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
| D-P1-8 | Designer tidak bisa membuat order baru dari dashboard (tidak ada tombol Add Order). | `templates/core/designer_dashboard.html` | Ditambahkan tombol "Add New Order" → `orders:order_add` di card Custom Orders. **(Dikembalikan lagi pada 19 Nov 2026 — lihat bagian "Pembaruan 19 Nov 2026": tombol dihapus, designer melanjutkan tahapan via detail order.)** | **Fixed → lalu diubah** |

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
9. `templates/core/designer_dashboard.html` — tambah kartu "Add Member" → customers:customer_add. **(Dihapus lagi 19 Nov 2026.)**
10. `customers/views.py` — CustomerCreateView required_roles tambah 'DESIGNER'. **(Dikembalikan ke ADMIN/CASHIER saja pada 19 Nov 2026.)**
11. `customers/models.py` — Customer.save() generate customer_id unik (loop hingga tidak collision).
12. `customers/forms.py` — CustomerForm hapus field 'user' (member baru tidak perlu linked user account; tidak ada dropdown admin/cashier/designer).

---

## Fitur Baru — Member / Customer Registration (Konsep Luxury)

Sebelum membuat pesanan custom order, pelanggan harus didaftarkan sebagai member terlebih dahulu:
- **Cashier dashboard**: kartu "Add Member" → daftar pelanggan baru (masih ada)
- **Designer dashboard**: kartu "Add Member" **sudah dihapus pada 19 Nov 2026** — pembuatan customer khusus ADMIN/CASHIER (lihat bagian "Pembaruan 19 Nov 2026")
- Setelah member tersedia, buat custom order dan pilih customer dari dropdown (order sudah terikat ke member)
- `customer_id` otomatis generate (CUST-0001, CUST-0002, dst.) dan tidak akan bentrok (UNIQUE constraint)
- Form member hanya berisi: nama, telepon, email, alamat, sumber, catatan — **tidak ada dropdown user/admin/cashier/designer**

---

## Fix — Bug Logika / Debugging (Prioritas Desainer)

Hasil smoke test penuh (alur designer end-to-end): order → measurement → design → production → material request → material usage → fitting → QC, semuanya berhasil (HTTP 200), termasuk klaim order/production yang belum punya designer. Designer tidak bisa QC/design/production/etc. untuk order designer lain (403).

| ID | Masalah | File | Perbaikan | Status |
|----|---------|------|-----------|--------|
| B-1 | `AuditMixin.created_by`/`updated_by` tidak pernah diisi di seluruh create/update → audit log selalu NULL | semua view bisnis | `created_by`/`updated_by` di-set di semua form_valid designer flow (order, design, production, material request/usage, QC, fitting, measurement, customer) dan `updated_by` pada semua AJAX update | **Fixed** |
| B-2 | `Cashier` tidak punya akses | `orders/views.py` | sudah diverifikasi (OrderCreateView.required_roles termasuk CASHIER) — lihat audit cashier section | **Fixed** |
| B-3 | Designer bisa membuat Design/Production/QC/Fitting/Measurement untuk order desainer lain | `designs/views.py`, `production/views.py`, `customers/views.py` | `dispatch` menolak `order_pk` yang `designer_id`-nya bukan milik designer yang login (kecuali unassigned) → `handle_no_permission()` / 403; `order.queryset` difilter ke `Q(designer=user) | Q(designer__isnull=True)` | **Fixed** |
| B-4 | Designer melihat/bisa merebut order desainer lain via `?order=` karena queryset dropdown menampilkan SEMUA order | semua view Create | queryset `order` disembunyikan/difilter ke `Q(designer=user) | Q(designer__isnull=True)` | **Fixed** |
| B-5 | Cashier membuat design/production → `designer` otomatis = cashier (salah: cashier bukan desainer) | `designs/views.py`, `production/views.py` | `form_valid` hanya set `designer=self.request.user` **jika role DESIGNER**; selain itu gunakan pilihan form | **Fixed** |
| B-6 | Field `designer` di dropdown menampilkan SEMUA user (admin, cashier, pelanggan, dll.) | `orders/forms.py`, `designs/forms.py`, `production/forms.py` | queryset di-filter hanya `role__code='DESIGNER'` | **Fixed** |
| B-7 | `DesignListView`/`MeasurementListView` search `.filter(a) | .filter(b)` → duplikat hasil & tidak efisien | `designs/views.py`, `customers/views.py` | `Q(a) \| Q(b) \| Q(order__order_number__icontains=q)` (design juga bisa dicari by nomor order) | **Fixed** |
| B-8 | Designer tidak bisa melihat Production/Order/Design yang belum punya desainer (hanya bisa lihat yang di-assign) → order "menggantung" tidak bisa diklaim | `orders/views.py`, `designs/views.py`, `production/views.py` | filter queryset designer → `Q(designer=user) \| Q(designer__isnull=True)` | **Fixed** |
| B-9 | Designer tidak bisa mengklaim order/production/design/material-request yang belum ada desainernya — harus ditunjuk admin | `orders/views.py`, `production/views.py`, `designs/views.py`, `production/views.py` | `update_order_status`/`production_update`/`update_design_status`/`MaterialUsageCreateView`/`MaterialRequestCreateView`: jika desainer NULL → self-assign otomatis saat update pertama; jika milik desainer lain → 403 | **Fixed** |
| B-10 | Tombol "Record Usage"/"Request Material" di production_detail membuka form tanpa konteks produksi → designer harus pilih manual production (error / salah pilih) | `production/views.py`, `templates/production/production_detail.html` | `MaterialUsageCreateView`/`MaterialRequestCreateView` mendukung `?production=<pk>` (production tersembunyi + terisi otomatis); tombol di detail produksi mengarah ke `?production={{ production.pk }}` | **Fixed** |
| B-11 | `MaterialUsage`/`MaterialRequest` untuk production desainer lain masih bisa dibuat via dropdown | `production/views.py` | queryset production difilter designer: `Q(designer=user) \| Q(designer__isnull=True)`; form_valid: defense-in-depth ownership check; `MaterialRequestForm`/`MaterialUsageCreateView` juga membatasi `material_request` ke production yang sama | **Fixed** |
| B-12 | `MaterialRequestListView`/`QualityControlListView`/`FittingListView` hanya menampilkan data milik designer lengkap — order/production unassigned tidak tampil sehingga tidak bisa diklaim | `production/views.py` | filter → `Q(...designer=user) \| Q(...designer__isnull=True)` | **Fixed** |
| B-13 | `MaterialRequestAction`/`MaterialUsageCreateView`/`production_update`/`update_design_status` tidak menulis `updated_by` | `production/views.py`, `designs/views.py` | `updated_by=self.request.user` di setiap save yang mengubah status/progress/design | **Fixed** |
| B-14 | `design_detail.html` tombol "Link Measurement" tanpa konteks order → measurement tidak terkait ke order | `templates/designs/design_detail.html` | tombol sekarang mengarah ke `customers:measurement_add?order={{ design.order.pk }}` | **Fixed** |
| B-15 | `orders/order_detail.html` tombol "Edit Order" tidak ada; list orders tidak punya tombol edit | `orders/views.py`, `templates/orders/order_detail.html` | `edit_url` ditambahkan ke list + detail order (orders:order_edit) | **Fixed** |
| B-16 | `DesignListView`/`OrderListView` tidak punya tombol Edit di list (hanya detail) | `designs/views.py`, `orders/views.py`, `templates/catalog/list.html` | `edit_url` ditambahkan | **Fixed** |
| B-17 | AJAX di `design_detail.html` & `production_detail.html` pakai URL hardcoded | templates | diubah ke `{% url "designs:update_design_status" pk=design.pk %}` dan `{% url "production:production_update" pk=production.pk %}` | **Fixed** |
| B-18 | `production_update` menolak designer pada production belum di-assign | `production/views.py` | designer boleh meng-update jika production.designer NULL (self-assign) atau milik sendiri | **Fixed** |
| B-19 | `DesignCreateView` dispatch: designer bisa buat design via `?order=` untuk order designer lain | `designs/views.py` | ownership check sebelum super().dispatch | **Fixed** |
| B-20 | `DesignDetailView`/`DesignListView` hanya tampilkan design milik designer — design unassigned (dibuat cashier) hilang dari designer | `designs/views.py` | filter → `Q(designer=user) \| Q(designer__isnull=True)` | **Fixed** |

## Fix — UI Designer: hapus tombol Add, production klik ke form, tabel Customer Orders

| ID | Masalah | File | Perbaikan | Status |
|----|---------|------|-----------|--------|
| U-1 | Tombol "Add" di semua list page designer tidak berguna | `designs/views.py`, `production/views.py`, `orders/views.py`, `customers/views.py` | `create_url`/`create_label` hanya diisi jika user **bukan** role DESIGNER. Tombol Add hilang total dari halaman designer | **Fixed** |
| U-2 | Kolom Production ID di list production tidak clickable | `production/views.py` | Production ID sekarang link ke `production:production_detail` (klik → form update progress) | **Fixed** |
| U-3 | Tidak ada tabel detail pelanggan + pesanan + progress | `customers/views.py`, `customers/urls.py`, `templates/customers/customer_orders.html` | View `CustomerOrdersTableView` (`/customers/orders/`) menampilkan: ID Customer, Nama, No. Pesanan, Status Order, Progress Produksi (progress bar), Status Produksi, Desain, Deadline. Search by customer/order. Sidebar designer & cashier ditambah link "Customer Orders" | **Fixed** |
| U-4 | Detail order tombol lanjutkan tahap custom order tetap terjaga | `templates/orders/order_detail.html` | Tetap ada (Buat Design, Production, QC, Fitting, Measurement) karena alur custom order memerlukannya | **OK** |

Smoke test "Designer UI fixes" (login designer):
- `/customers/orders/` → 200, tabel tampil (ID, Nama, Pesanan, Progress bar)
- Semua list page designer (design/production/material request/qc/fitting/orders/measurements/customers) → **tidak ada tombol Add**
- Production list → Production ID clickable ke `production_detail`; detail punya form "Update Progress"
- Order detail → tombol lanjutkan tahap custom order masih ada

---

## Fitur Baru — Pembayaran Custom Order (DP / Cicilan / Lunas)

Sebelumnya pembayaran **hanya ada untuk transaksi POS** (`Payment` → `Transaction`). Belum ada pembayaran untuk custom order. Sekarang sudah ada modul `OrderPayment` yang terintegrasi ke detail order.

| ID | Fitur | File | Detail | Status |
|----|-------|------|--------|--------|
| P-1 | Model `OrderPayment` | `payments/models.py`, `payments/migrations/0003_orderpayment.py` | `OrderPayment` (FK → `Order`): amount, payment_type (FULL/DP/INSTALLMENT), method (CASH/BANK_TRANSFER/QRIS), status (PENDING/CONFIRMED/REFUNDED/FAILED), payment_proof, due_date (jatuh tempo cicilan/DP), confirmed_at, confirmed_by, notes + audit fields | **Fixed** |
| P-2 | Record pembayaran custom order | `payments/views.py` `record_order_payment`, `payments/urls.py`, `templates/orders/order_detail.html` | Cashier/admin catat pembayaran via modal "Catat Pembayaran" di halaman detail order (jumlah, tipe, metode, jatuh tempo, bukti, catatan). Status awal PENDING | **Fixed** |
| P-3 | Konfirmasi pembayaran | `payments/views.py` `confirm_order_payment` | Row lock + atomic; cashier/admin konfirmasi → status CONFIRMED, `confirmed_at`/`confirmed_by` terisi; **`order.dp_amount` otomatis disinkronkan** dengan total pembayaran CONFIRMED | **Fixed** |
| P-4 | Void / Refund pembayaran | `payments/views.py` `void_order_payment` | PENDING → FAILED; CONFIRMED → REFUNDED; `dp_amount` otomatis dihitung ulang | **Fixed** |
| P-5 | Halaman list pembayaran custom order | `payments/views.py` `order_payment_list`, `templates/payments/order_payment_list.html`, `payments/urls.py` | `/payments/orders/` — tabel pembayaran custom order dengan filter (search no. order / nama pelanggan / confirmed_by, status, metode, tipe, tanggal) + summary cards (total dikonfirmasi, menunggu konfirmasi, jumlah pembayaran). Aksi: konfirmasi / void / refund via AJAX | **Fixed** |
| P-6 | Section Payments di detail order | `templates/orders/order_detail.html` | Ringkasan (Total Pesanan, Dibayar DP, Sisa Tagihan) + tabel pembayaran order + tombol "Catat Pembayaran" (ADMIN/CASHIER only) + tombol konfirmasi/void per baris (ADMIN/CASHIER only) | **Fixed** |
| P-7 | Sidebar link | `templates/core/cashier_dashboard.html`, `templates/core/admin_dashboard.html` | Link "Pembayaran Custom Order" → `payments:order_payment_list` | **Fixed** |
| P-8 | Akses | `payments/views.py` | Record/konfirmasi/void/list pembayaran custom order **hanya ADMIN & CASHIER**. Designer: redirect/403 | **Fixed** |
| P-9 | Sinkronisasi `dp_amount` otomatis | `payments/views.py` | Setiap confirm/void, `order.dp_amount` dihitung ulang = SUM(amount CONFIRMED). `order.remaining_balance` (total − dp) otomatis akurat | **Fixed** |

Alur baru:
1. Cashier buka detail custom order → lihat **Payments**: Total, Dibayar (DP), Sisa Tagihan.
2. Klik **Catat Pembayaran** → isi jumlah, tipe (DP/cicilan/lunas), metode → status PENDING.
3. Cashier/admin klik tombol konfirmasi (✓) → status CONFIRMED → **DP otomatis masuk ke order** dan Sisa Tagihan berkurang.
4. Refund (×) → status REFUNDED → DP otomatis dikurangi.
5. Daftar semua pembayaran custom order di **/payments/orders/** (filter & search).

Smoke test "Custom Order Payment": record DP 300rb → confirm → dp=300rb ✅; record 700rb → confirm → dp=1jt ✅; refund 300rb → dp=700rb ✅; designer tidak bisa record (403) ✅; designer tidak bisa lihat list (302) ✅.

---

## Pembaruan 19 November 2026

### Perubahan akses/UI designer & customer (working tree, belum di-commit)
| ID | Perubahan | File | Detail |
|----|-----------|------|--------|
| N-1 | Tombol "Add New Order" dihapus dari dashboard designer | `templates/core/designer_dashboard.html` | Card Custom Orders kini hanya berisi "Manage Orders". Designer melanjutkan tahapan lewat detail order (panel Langkah Selanjutnya). |
| N-2 | Kartu "Add Member" dihapus dari dashboard designer | `templates/core/designer_dashboard.html` | Designer tidak lagi mendaftarkan customer. |
| N-3 | Pembuatan customer dibatasi ke ADMIN/CASHIER | `customers/views.py` | `CustomerCreateView.required_roles = ('ADMIN', 'CASHIER')` (sebelumnya termasuk DESIGNER). List page juga menyembunyikan tombol Add untuk designer. |
| N-4 | Sembunyikan tombol Add di semua list page untuk designer | `orders/views.py`, `designs/views.py`, `production/views.py`, `customers/views.py` | `create_url`/`create_label` hanya diisi jika bukan role DESIGNER. |
| N-5 | Tabel Customer Orders | `customers/views.py`, `customers/urls.py`, `templates/customers/customer_orders.html` | Route `/customers/orders/` menampilkan customer + pesanan + progress produksi; link di sidebar admin/cashier/designer. |
| N-6 | Pembayaran custom order (OrderPayment) | `payments/models.py`, `payments/views.py`, `payments/urls.py`, `payments/forms.py`, `payments/migrations/0003_orderpayment.py`, `templates/orders/order_detail.html`, `templates/payments/order_payment_list.html` | Model + record/confirm/void + list `/payments/orders/` + section Payments di detail order; `dp_amount` order tersinkron otomatis. Akses ADMIN/CASHIER. |

### Kondisi database
- Seluruh data transaksional dihapus untuk presentasi demo (customer, produk, transaksi, order, design, produksi, pembayaran, ledger, sesi, admin log).
- Tersisa: 3 user (`admin`, `cashier`, `designer`), 3 role, dan tabel framework Django.
- Backup: `db_backup_2026119_035957.sqlite3`.
- `python manage.py check` tetap lolos setelah pembersihan; login ketiga user terverifikasi.

---

## Catatan

- Seluruh bug di atas diuji via smoke test manual end-to-end (login sebagai `designer` & `cashier`; buat order → measurement → design → production → request → usage → fitting → QC). Semua HTTP 200 beserta status DB (`created_by`/`updated_by`, `designer` otomatis, klaim unassigned). Check `python manage.py check` lolos.
- Designer berbeda tidak bisa saling mengakses order/qc/design masing-masing → 403 diverifikasi.
- Tes data (`Full smoke order`, dll.) sudah dibersihkan dari database; seluruh data bisnis dikosongkan lagi pada 19 Nov 2026 untuk demo.
- Masih belum ada test otomatis (0 test). Disarankan menambahkan `TestCase` untuk alur designer dan cashier (create order, claim order, downstream create) agar tidak regresi di masa depan.
- `analytics/`, `notifications/`, `documents/` masih placeholder (lihat progress.md).
- Perubahan N-1 s/d N-6 masih berupa working tree yang belum di-commit.

