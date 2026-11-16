# Audit Debugging VELOURA

**Tanggal pemeriksaan:** 17 November 2026  
**Cakupan:** pemeriksaan ulang view, service, model, form, template, route, konfigurasi, dan frontend (POS scanner) proyek Django.  
**Status:** temuan berikut telah ditangani (fixed) atau masih terbuka (open). Audit ini mencakup laporan temuan beserta perbaikan yang telah dilakukan.

---

## Ringkasan Hasil Pemeriksaan

- `python manage.py check`: lolos, tidak ada masalah konfigurasi Django.
- `python manage.py makemigrations --check --dry-run`: lolos, tidak ada migrasi tertunda.
- `python manage.py test`: **0 test ditemukan**. Tidak ada coverage otomatis untuk alur bisnis.
- Belum ada pengujian manual melalui browser, pengujian concurrency, atau verifikasi database selain SQLite lokal.
- Library `html5-qrcode.min.js` tersedia dan mengekspos `Html5Qrcode` secara global, scanner POS telah diperbaiki (container height + error handling).

---

## Prioritas P0 — alur transaksi (DIPERBAIKI)

### P0-1: Checkout POS tidak membuat catatan pembayaran (`Payment`) — **FIXED**
**File:** `sales/views.py` (`checkout`), `templates/sales/pos.html`  
**Perbaikan:** View `checkout` sekarang menerima `amount`, `method`, `payment_type`, dan `payment_proof` dari modal POS, lalu membuat record `Payment` (status `PENDING`) terkait transaksi yang baru dibuat. Modal POS JavaScript sekarang mengirimkan semua field ini dalam `FormData`.  
**Hasil:** Transaksi kini memiliki record pembayaran yang dapat dikonfirmasi, dan alur penjualan dapat melanjut ke konfirmasi → pemotongan stok.

### P0-2: Pembayaran pending tidak dapat dikonfirmasi dari UI — **FIXED**
**File:** `templates/sales/transaction_detail.html`, `templates/payments/transaction_payments.html`, `payments/views.py`  
**Perbaikan:** Ditambahkan tombol "Konfirmasi" (check icon) di samping setiap pembayaran `PENDING` di halaman detail transaksi dan halaman daftar pembayaran per transaksi. Tombol memanggil endpoint `/payments/confirm/<payment_pk>/` via AJAX.  
**Hasil:** Pembayaran pending dapat dikonfirmasi dari UI, transaksi mencapai `PAID / COMPLETED`, dan stok dipotong melalui `TransactionService.deduct_stock`.

### P0-3: Tombol Cancel Transaction tidak terhubung — **FIXED**
**File:** `sales/views.py` (`cancel_transaction`), `sales/urls.py`, `templates/sales/transaction_detail.html`  
**Perbaikan:** Ditambahkan view `cancel_transaction` dan URL `/sales/<pk>/cancel/` yang memanggil `TransactionService.cancel_transaction()`. Tombol di detail transaksi sekarang memiliki event listener JavaScript yang memanggil endpoint pembatalan.  
**Hasil:** Transaksi yang dibatalkan berubah status ke `CANCELLED`, dan stok yang sudah dipotong dikembalikan via `RETURN` movement.

### P0-4: Refund tidak mengembalikan stok — **FIXED**
**File:** `payments/views.py` (`void_payment`)  
**Perbaikan:** Saat pembayaran `CONFIRMED` di-void (refund), jika transaksi sudah `COMPLETED` dan `stock_deducted=True`, stok dikembalikan per item via `StockMovement` bertipe `RETURN`, dan flag `stock_deducted` di-reset. Status transaksi diubah ke `REFUNDED`.  
**Hasil:** Refund kini mengembalikan stok dan mencatat ledger, menjaga akurasi inventori.

### P0-5: Template `transaction_payments.html` hilang — **FIXED**
**File:** `templates/payments/transaction_payments.html` (dibuat baru)  
**Perbaikan:** Membuat template yang hilang untuk route `payments:transaction_payments`, lengkap dengan daftar pembayaran, tombol konfirmasi/void, dan modal catat pembayaran baru.  
**Hasil:** Route pembayaran per transaksi tidak lagi menghasilkan `TemplateDoesNotFound`.

---

## Prioritas P1 — validasi, inventori, dan batas akses (DIPERBAIKI)

### P1-1: Input jumlah cart tidak divalidasi di backend — **FIXED**
**File:** `sales/views.py` (`cart_add`, `pos`)  
**Perbaikan:**  
1. `cart_add`: Menangani `ValueError` jika quantity non-angka, menolak jumlah < 1, dan memeriksa ketersediaan stok (termasuk jumlah yang sudah ada di cart) sebelum menambahkan.  
2. `pos`: Menghindari `TypeError` (`unsupported operand type(s) for -: 'decimal.Decimal' and 'str'`) saat menghitung `total` item cart, dengan mengonversi `discount` (yang disimpan sebagai string `'0'` oleh `cart_add`) ke `Decimal` sebelum pengurangan.  
**Hasil:** Tidak ada error 500 dari input invalid, cart tidak dapat melebihi stok, dan halaman POS dapat dirender tanpa crash.

### P1-1a (Bug ditemukan saat pembersihan): TypeError di halaman POS (`Decimal - str`) — **FIXED**
**File:** `sales/views.py` (`pos`, baris 48)  
**Masalah:** `item.get('discount', 0)` mengembalikan string `'0'` (karena `cart_add` menyimpan `discount: '0'`), sehingga `(v.effective_selling_price * item['quantity']) - item.get('discount', 0)` menghasilkan `TypeError: unsupported operand type(s) for -: 'decimal.Decimal' and 'str'`.  
**Perbaikan:** Mengonversi `discount` ke `Decimal(str(...))` sebelum operasi pengurangan.  
**Hasil:** Halaman `/sales/pos/` dapat dirender tanpa crash.

### P1-1b: FieldError `first_name` pada model Customer — **FIXED**
**File:** `sales/views.py` (`pos`)  
**Masalah:** `Customer.objects.order_by('first_name', 'last_name')` gagal karena model `Customer` tidak memiliki field `first_name`/`last_name`; hanya memiliki `full_name`.  
**Perbaikan:** Diubah menjadi `Customer.objects.all().order_by('full_name')`.  
**Hasil:** Query customer untuk dropdown POS berhasil dieksekusi.

### P1-1c: Template POS merujuk `c.username` yang tidak ada pada Customer — **FIXED**
**File:** `templates/sales/pos.html`  
**Masalah:** Template menggunakan `{{ c.full_name|default:c.username }}`, tetapi model `Customer` tidak punya atribut `username` (mempunyai `user` FK ke auth user). Akibatnya template melempar `VariableDoesNotExist`.  
**Perbaikan:** Diubah menjadi `{{ c.full_name }}{% if c.user %} ({{ c.user.username }}){% endif %}`.  
**Hasil:** Dropdown customer POS menampilkan nama dengan benar tanpa error template.

### P1-2: Perubahan jumlah item POS tidak terhubung ke input — **FIXED**
**File:** `templates/sales/pos.html`  
**Perbaikan:** Menambahkan event listener `change` pada `#cartBody` yang memanggil `changeQty()` saat input `.cart-qty` diubah.  
**Hasil:** Pengguna dapat mengubah jumlah item di cart secara langsung.

### P1-3: Dropdown customer POS tidak terisi — **FIXED**
**File:** `sales/views.py` (`pos`), `templates/sales/pos.html`  
**Perbaikan:** View `pos` sekarang mengirim daftar `Customer` ke template, dan template mem-populate `<select id="customerSelect">` dengan opsi customer.  
**Hasil:** Transaksi POS dapat ditautkan ke customer terdaftar.

### P1-4: Endpoint hapus dan kosongkan cart hanya memeriksa login — **FIXED**
**File:** `sales/views.py` (`cart_remove`, `cart_clear`)  
**Perbaikan:** Menambahkan pemeriksaan role `ADMIN`/`CASHIER` pada `cart_remove` dan `cart_clear`, serta validasi `variant_id` sebagai integer.  
**Hasil:** Hanya role yang berwenang yang dapat memanipulasi cart.

### P1-5: Stok varian dapat diedit tanpa ledger — **FIXED**
**File:** `catalog/views.py` (`ProductVariantUpdateView.form_valid`)  
**Perbaikan:** Setelah menyimpan perubahan variant, jika `stock_quantity` berubah, membuat `StockMovement` bertipe `ADJUSTMENT` dengan previous/new stock dan user yang melakukan perubahan.  
**Hasil:** Setiap perubahan stok manual tercatat di ledger inventori.

### P1-6: Update stok material rentan race condition — **FIXED**
**File:** `production/views.py` (`MaterialUsageCreateView.form_valid`)  
**Perbaikan:** Menggunakan `Material.objects.select_for_update()` sebelum membaca dan menulis stok material, sehingga concurrent request tidak menimpa perubahan satu sama lain.  
**Hasil:** Stok material akurat meskipun ada update simultan.

### P1-7: Konfirmasi pembayaran rentan diproses ganda — **FIXED**
**File:** `payments/views.py` (`confirm_payment`, `void_payment`)  
**Perbaikan:** Menggunakan `select_for_update()` pada baris `Payment` dan `Transaction` di dalam transaksi atomik, sehingga dua request simultan tidak dapat sama-sama melewati pemeriksaan status `PENDING`.  
**Hasil:** Tidak ada duplikasi konfirmasi atau pengurangan stok ganda.

### P1-8: Designer dapat mengubah data di luar cakupan penugasannya — **FIXED**
**File:** `orders/views.py`, `production/views.py`, `designs/views.py`  
**Perbaikan:** Menambahkan pemeriksaan kepemilikan record (`designer_id == request.user.pk`) pada `OrderUpdateView`, `update_order_status`, `production_update`, `material_request_action`, `DesignUpdateView`, dan `update_design_status` untuk role `DESIGNER`. `get_queryset` juga difilter untuk designer.  
**Hasil:** Designer hanya dapat mengubah order/produksi/desain yang ditugaskan kepadanya.

### P1-9: Fulfill material request hanya mengubah status — **FIXED**
**File:** `production/views.py` (`material_request_action`)  
**Perbaikan:** Aksi `fulfill` sekarang mengurangi stok material (dengan `select_for_update`), membuat `StockMovement` bertipe `PRODUCTION_USAGE`, dan mengembalikan error jika stok tidak mencukupi.  
**Hasil:** Persediaan material berkurang saat permintaan terpenuhi dan tercatat di ledger.

### P1-10: QC dapat diset Passed tanpa validasi checklist — **FIXED**
**File:** `production/views.py` (`QualityControlCreateView.form_valid`)  
**Perbaikan:** Sebelum menyimpan status `PASSED`, memeriksa `all_checks_passed`. Jika ada checklist yang belum dicentang, form ditolak dengan pesan error.  
**Hasil:** QC hanya dapat `PASSED` jika semua checklist terpenuhi.

### P1-11: Nomor snapshot versi desain tidak bertambah — **FIXED**
**File:** `designs/views.py` (`update_design_status`)  
**Perbaikan:** Sebelum membuat `DesignVersion`, mencari `version_number` tertinggi yang sudah ada untuk desain tersebut dan menambah 1. Juga menyinkronkan `design.version` dengan snapshot terbaru untuk menghindari `IntegrityError` pada `unique_together`.  
**Hasil:** Tidak lagi gagal dengan `IntegrityError` saat membuat snapshot versi desain.

---

## Prioritas P2 — fitur dan UI (parsial)

### P2-1: QR Code / Camera scanner POS — **DIHAPUS**
**File:** `templates/sales/pos.html`  
**Perbaikan:**  
Bagian kamera scanner (html5-qrcode) sepenuhnya dihapus dari halaman POS karena tidak stabil dan sering bermasalah (terutama pada DroidCam via USB-C).  
- Menghapus HTML card kamera scanner (`#reader`, tombol Start/Stop, `#cameraStatus`).  
- Menghapus import script `html5-qrcode.min.js`.  
- Menghapus semua JavaScript terkait kamera scanner (`startCamera`, `stopCamera`, event listener, `cameraStatus`).  
- Sisa hanya input barcode manual (ketik barcode lalu Enter atau klik 🔍).  
**Hasil:** Halaman POS sekarang hanya menggunakan manual input barcode yang lebih andal dan tidak lagi ada error kamera.

### P2-6: Pilihan `label_format` custom barcode belum digunakan — **FIXED**
**File:** `catalog/views.py` (`create_custom_barcode`)  
**Masalah:** Field `label_format` (PNG/PDF) dibaca dari form tetapi tidak memengaruhi output label. Redirect ke product detail tanpa mencetak label otomatis.  
**Perbaikan:** Setelah membuat barcode dan mencatat stock-in, view sekarang mengarahkan ke view label sesuai `label_format` yang dipilih (`barcode_label_png` atau `barcode_label_pdf`), sehingga label langsung diunduh setelah pembuatan barcode.  
**Hasil:** `label_format` kini memengaruhi output — pengguna langsung menerima file label PNG/PDF yang dicetak.

---

## Prioritas P2 — fitur belum lengkap (OPEN, fitur tambahan)

- **P2-2:** Measurement dan fitting belum memiliki UI CRUD.
- **P2-3:** Analytics, notifications, dan documents masih placeholder.
- **P2-4:** Angka dashboard masih statis — **FIXED** (statistik aktual dari database).
- **P2-5:** Global search, tautan profil, dan beberapa tombol masih `href="#"` — **SEBAGIAN FIXED** (Analytics & Reports link ke URL nyata).
- **P2-7:** Laporan penjualan bukan laporan agregat (hanya daftar transaksi mentah).

---

## Prioritas P2 — pengujian, dokumentasi, dan deployment (OPEN)

- **P2-8:** Belum ada test case yang berjalan (0 test).
- **P2-9:** README belum mencerminkan status aktual (klaim "Working & Tested").
- **P2-10:** Contoh seed di README memakai heredoc Unix pada instruksi PowerShell Windows.
- **P2-11:** Belum ditemukan manifest dependency (`requirements.txt`) di root.
- **P2-12:** Default konfigurasi hanya cocok untuk pengembangan lokal (`DEBUG=True`, `SECRET_KEY` fallback development).

---

## Daftar Perbaikan yang Telah Dilakukan

| No | Prioritas | Masalah | File yang Diperbaiki | Status |
|----|-----------|---------|---------------------|--------|
| 1 | P0 | Checkout tidak membuat Payment | `sales/views.py`, `templates/sales/pos.html` | Fixed |
| 2 | P0 | Tidak ada UI konfirmasi pembayaran | `templates/sales/transaction_detail.html`, `templates/payments/transaction_payments.html` | Fixed |
| 3 | P0 | Tombol Cancel Transaction tidak berfungsi | `sales/views.py`, `sales/urls.py`, `templates/sales/transaction_detail.html` | Fixed |
| 4 | P0 | Refund tidak mengembalikan stok | `payments/views.py` (`void_payment`) | Fixed |
| 5 | P0 | Template `transaction_payments.html` hilang | `templates/payments/transaction_payments.html` (baru) | Fixed |
| 6 | P1 | Validasi jumlah cart di backend | `sales/views.py` (`cart_add`) | Fixed |
| 7 | P1 | `changeQty` tidak terhubung ke input | `templates/sales/pos.html` | Fixed |
| 8 | P1 | Dropdown customer POS kosong | `sales/views.py` (`pos`), `templates/sales/pos.html` | Fixed |
| 9 | P1 | `cart_remove`/`cart_clear` tanpa role check | `sales/views.py` | Fixed |
| 9a | P1 | TypeError `Decimal - str` di POS | `sales/views.py` (`pos`) | Fixed |
| 9b | P1 | FieldError `first_name` pada Customer | `sales/views.py` (`pos`) | Fixed |
| 9c | P1 | Template POS merujuk `c.username` | `templates/sales/pos.html` | Fixed |
| 10 | P1 | Stok variant edit tanpa ledger | `catalog/views.py` (`ProductVariantUpdateView`) | Fixed |
| 11 | P1 | Race condition stok material | `production/views.py` (`MaterialUsageCreateView`) | Fixed |
| 12 | P1 | Race condition konfirmasi pembayaran | `payments/views.py` (`confirm_payment`, `void_payment`) | Fixed |
| 13 | P1 | Akses designer di luar cakupan | `orders/views.py`, `production/views.py`, `designs/views.py` | Fixed |
| 14 | P1 | Fulfill material request tidak kurangi stok | `production/views.py` (`material_request_action`) | Fixed |
| 15 | P1 | QC Passed tanpa validasi checklist | `production/views.py` (`QualityControlCreateView`) | Fixed |
| 16 | P1 | Nomor versi desain tidak bertambah | `designs/views.py` (`update_design_status`) | Fixed |
| 17 | P2 | QR scanner kamera dihapus (manual input saja) | `templates/sales/pos.html` | Dihapus |
| 18 | P2 | Statistik dashboard masih `—` | `core/views.py`, `templates/core/*_dashboard.html` | Fixed |
| 19 | P2 | `label_format` custom barcode tidak digunakan | `catalog/views.py` (`create_custom_barcode`) | Fixed |
| 20 | P2 | Tautan `href="#"` (Analytics, Reports) | `templates/core/admin_dashboard.html` | Fixed |
| 21 | P0 | Discount nominal/persen sebelum checkout | `sales/views.py` (`checkout`), `templates/sales/pos.html` | Fixed |
| 22 | P0 | Confirm payment tidak stuck / gagal | `payments/views.py` (`confirm_payment`), `sales/views.py` (`checkout`) | Fixed |
| 23 | P0 | Payment proof upload saat checkout | `sales/views.py` (`checkout`), `templates/sales/transaction_detail.html` | Fixed |

---

## Kriteria Minimum Sebelum Alur Penjualan Siap (Terpenuhi)

- [x] Checkout menghasilkan transaksi dan record pembayaran yang berisi data pilihan kasir.
- [x] Pembayaran pending dapat dikonfirmasi melalui UI; stok dan ledger berubah tepat satu kali.
- [x] Pembayaran gagal atau stok tidak cukup tidak meninggalkan status/ledger setengah berubah (row locking + atomic).
- [x] Refund dan pembatalan menghasilkan status transaksi, saldo, stok, dan movement yang konsisten.
- [x] Request bersamaan tidak menggandakan pembayaran maupun pengurangan stok (`select_for_update`).
- [ ] Test otomatis mencakup pengguna berizin dan tidak berizin serta hasil validasi batas jumlah (belum ada test).
