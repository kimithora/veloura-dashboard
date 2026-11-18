# Progress VELOURA Dashboard

**Pembaruan:** 19 November 2026  
**Status keseluruhan:** alur POS dan pembayaran sudah end-to-end, workflow custom order (designer) sudah lengkap dan lolos smoke test. Belum ada test otomatis. Database sedang dikosongkan untuk demo.  
**Catatan:** status fase mengacu pada kode yang diperiksa, bukan rencana awal. Temuan rinci dan urutan debugging ada di [audit.md](./audit.md); skema database ada di [ERD.md](./ERD.md).

## Ringkasan fase

| Fase | Status | Ringkasan |
|---|---|---|
| 0. Persiapan proyek | Selesai untuk pengembangan lokal | Project Django, app modular, SQLite, routing, template dasar tersedia. Deployment dan setup lintas mesin belum diverifikasi. |
| 1. Fondasi sistem | Sebagian selesai | Custom user, role, login, dashboard, dan pembatasan akses backend tersedia. Test role/route masih 0. |
| 2. Katalog dan inventori | Sebagian selesai | Model katalog, varian, customer, supplier, material, serta ledger tersedia. Sebagian perubahan stok via form tidak membuat ledger; concurrency sebagian sudah pakai row lock. |
| 3. POS dan transaksi | Selesai (end-to-end, tanpa tes otomatis) | Checkout menyimpan pembayaran dari modal POS, cart tervalidasi, pembatalan tersambung dari UI, stok dipotong saat konfirmasi dan dikembalikan saat void/cancel. |
| 4. Pembayaran dan invoice | Selesai (POS + custom order) | Record/konfirmasi/void/refund transaksi POS plus invoice PDF. **Baru:** modul `OrderPayment` untuk DP/cicilan/lunas custom order dengan sinkronisasi `dp_amount` otomatis. |
| 5. Custom order, desain, produksi | Selesai untuk smoke test manual | Order → measurement → design (versi) → production → material request/usage → fitting → QC berjalan; klaim order/production unassigned; pembatasan milik designer konsisten; tombol Add disembunyikan untuk designer. |
| 6. Analytics dan fitur pendukung | Belum selesai | Analytics, notifications, documents masih placeholder. Statistik dashboard, pencarian global, dan laporan sebagian belum ada. |

## Fase 0 — Persiapan proyek

### Sudah tersedia
- Project Django dengan app modular dan konfigurasi database SQLite untuk pengembangan.
- Routing utama, template dasar, serta asset frontend.

### Masih perlu
- Manifest dependency (`requirements.txt`/`pyproject.toml`) agar lingkungan dapat direproduksi — saat ini belum ada.
- Konfigurasi deployment dengan secret, `DEBUG`, dan host production yang eksplisit.

## Fase 1 — Fondasi sistem

### Sudah tersedia
- Custom user dan role ADMIN, CASHIER, DESIGNER.
- Login/logout serta dashboard berbasis role.
- Pembatasan role backend pada semua view bisnis (`RoleRequiredMixin` / cek `has_role`).

### Masih perlu
- Test otomatis untuk role yang diizinkan/ditolak.

## Fase 2 — Katalog dan inventori

### Sudah tersedia
- Produk, varian, barcode, customer, supplier, material, dan stock movement.
- Fulfill material request dan material usage sudah mengurangi stok + mencatat ledger dengan row lock.

### Masih perlu
- Form create/edit Material dan stok awal varian tidak membuat ledger (hanya perubahan lewat endpoint adjust/usage/fulfill yang tercatat).
- Sinkronkan perubahan barcode varian dengan registry barcode secara konsisten.

## Fase 3 — POS dan transaksi

### Sudah tersedia
- Scanner/lookup barcode, session cart, checkout transaksi pending, detail transaksi, dan invoice PDF.
- Checkout menyimpan pembayaran yang dipilih pada modal POS (method, tipe, jumlah).
- Pembatalan transaksi tersambung dari UI (`Cancel Transaction` saat PENDING) dan mengembalikan stok via ledger RETURN.

### Masih perlu
- Tes alur sukses, pembayaran parsial, stok tidak cukup, pembatalan, dan request duplikat (masih manual).

## Fase 4 — Pembayaran dan invoice

### Sudah tersedia
- Model dan form pencatatan pembayaran POS, endpoint konfirmasi/refund, UI konfirmasi/void, invoice PDF.
- Refund mengembalikan stok dan menyelaraskan status transaksi, termasuk skenario multi-pembayaran.
- **OrderPayment (baru):** pembayaran custom order (DP/cicilan/lunas) dengan record/confirm/void, list `/payments/orders/` berfilter, section Payments di detail order, dan sinkronisasi otomatis `order.dp_amount` + `remaining_balance`. Hanya ADMIN/CASHIER.

### Masih perlu
- Test untuk status pembayaran, pembayaran parsial, dan concurrency.

## Fase 5 — Custom order, desain, dan produksi

### Sudah tersedia
- Order create/edit/status + history; designer dapat membuat order (auto-assign) dan mengklaim order unassigned.
- Measurement (dengan preselect `?order=`), Design + version snapshot (approve → status order naik), Production + progress, MaterialRequest approve/reject/fulfill (stok berkurang), MaterialUsage (stok berkurang), Fitting, QC (checklist wajib lolos sebelum PASSED).
- Dropdown `designer` difilter hanya role DESIGNER; `created_by`/`updated_by` terisi di semua create/update.
- Designer hanya melihat/mengelola record miliknya atau unassigned (queryset `Q(designer=user) | Q(designer__isnull=True)`); milik designer lain → 403.
- Tombol Add di semua list page disembunyikan untuk designer; designer melanjutkan tahapan via panel "Langkah Selanjutnya" di detail order.
- Tabel Customer Orders (`/customers/orders/`) dengan progress bar produksi.
- Pembuatan customer kini **khusus ADMIN/CASHIER** (designer tidak bisa menambah customer).

### Masih perlu
- Test otomatis untuk alur designer end-to-end.
- Edit form biasa pada order/design tidak menulis history/snapshot (hanya endpoint AJAX).

## Fase 6 — Analytics dan fitur pendukung

### Status
- `analytics/`, `notifications/`, `documents/` masih placeholder.
- Statistik dashboard ADMIN/CASHIER/DESIGNER sudah memakai data riil (bukan placeholder), tetapi pencarian global, laporan, dan notifikasi in-app belum ada.

## Kondisi database (19 November 2026)

- Seluruh data transaksional **dihapus untuk keperluan presentasi demo**: customer, produk, varian, barcode, brand, category, supplier, material, stock movement, transaksi POS + item, pembayaran, order + history, design + version, production, material request/usage, fitting, QC, sesi login, dan admin log.
- **Tersisa hanya:** 3 user (`admin`, `cashier`, `designer`) + 3 role (ADMIN, CASHIER, DESIGNER) + tabel framework Django (migrations, content types, permissions).
- Backup sebelum pembersihan: `db_backup_20261119_035957.sqlite3`.
- `django_session` ikut dikosongkan → semua sesi lama logout.

## Pemeriksaan terakhir

- Django system check: **lolos (0 issues)**.
- `makemigrations --check`: **tidak ada perubahan tertunda**.
- Django test runner: **0 test ditemukan**.
- Verifikasi pasca-pembersihan DB: login ketiga user tetap dikenali, `Role` tetap ada.

## Prioritas kerja berikutnya

1. Tambahkan test otomatis untuk alur POS/pembayaran dan workflow designer.
2. Buat `requirements.txt`/`pyproject.toml` agar setup dapat direproduksi.
3. Lengkapi analytics/notifications/documents atau hapus placeholder UI yang mengganggu demo.
4. Isi ulang data contoh bila diperlukan setelah presentasi (atau restore backup).
5. Perbarui konfigurasi deployment (secret, DEBUG, host) sebelum dipakai di luar lokal.
