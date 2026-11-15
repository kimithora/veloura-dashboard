# Progress VELOURA Dashboard

Dokumen ini berisi ringkasan perkembangan proyek, status pekerjaan yang sudah selesai, serta item yang masih belum dikerjakan. Struktur dibuat per fase agar mudah dipantau dan dikembangkan secara bertahap.

---

## Phase 0 — Persiapan Awal

Status: Selesai

### Yang sudah selesai
- Proyek Django telah dibuat dengan struktur aplikasi modular.
- Terdapat project utama `config/` serta berbagai app seperti:
  - `accounts/`
  - `catalog/`
  - `customers/`
  - `suppliers/`
  - `inventory/`
  - `sales/`
  - `payments/`
  - `core/`
  - dll.
- Database SQLite sudah aktif (`db.sqlite3`).
- Konfigurasi dasar app dan routing project sudah terbentuk.
- Template dasar untuk UI sudah dibuat di `templates/`.
- File CSS/JS statis sudah mulai disiapkan di `static/`.

### Detail implementasi
- Setup project backend Python Django.
- Pengaturan project settings dan koneksi lokal.
- Struktur aplikasi siap untuk pengembangan fitur bisnis.

### Yang belum selesai
- Dokumentasi setup developer yang lebih lengkap untuk tim.
- Verifikasi lingkungan baru di mesin lain.
- Penetapan alur deployment dan konfigurasi production.

---

## Phase 1 — Fondasi Sistem

Status: Selesai

### Yang sudah selesai
- Django project dan 14 modular app telah dibuat.
- Custom user model dibuat dan digunakan di `accounts/`.
- Sistem peran pengguna telah dibuat:
  - `ADMIN`
  - `CASHIER`
  - `DESIGNER`
- Role-based authorization diterapkan di backend.
- Login dan logout sudah tersedia.
- Session handling sudah berjalan.
- Dashboard per role sudah dibuat:
  - Admin dashboard
  - Cashier dashboard
  - Designer dashboard
- Sidebar navigasi, top bar, dan dropdown profile telah dibuat.
- UI umum menggunakan Bootstrap 5 dan custom CSS.

### Detail implementasi
- User dibatasi aksesnya berdasarkan role, bukan sekadar menyembunyikan tombol di frontend.
- Role dan hak akses ditangani di logic aplikasi dan middleware/permission.
- Template dasar `base.html` menjadi layout umum semua halaman.

### Yang belum selesai
- Validasi akses setiap route secara lebih menyeluruh untuk semua role.
- Penambahan unit test untuk autentikasi dan role permissions.
- Pembersihan bug kecil UI/UX pada beberapa halaman.

---

## Phase 2 — Katalog dan Inventori

Status: Selesai sebagian / mayoritas selesai

### Yang sudah selesai
- Model katalog produk sudah dibuat.
- Produk mencakup:
  - SKU
  - source produk (Veloura Original / Third-Party Purchased / Third-Party Consignment)
  - supplier
  - harga
  - stok
  - image
  - status
- Product variant sudah dibuat untuk variasi ukuran, warna, dan barcode.
- Barcode registry untuk produk sudah disiapkan.
- Data customer dibuat dan dapat dikaitkan dengan histori pembelian.
- Data supplier dibuat untuk pembelian langsung maupun konsinyasi.
- Material/raw stock management sudah dibuat.
- Stock movement ledger sudah ada untuk:
  - purchase
  - sales
  - production usage
  - output
  - return
  - adjustment
  - damage/loss

### Detail implementasi
- Ledger mencatat perubahan stok secara historis.
- Setiap pergerakan stok mempunyai referensi, user, timestamp, dan data sebelum/sesudah perubahan.
- Struktur ini penting untuk menjaga integritas data inventory.

### Yang belum selesai
- Validasi stok untuk semua alur transaksi masih perlu diuji lebih luas.
- Pembuatan laporan inventory detail per item masih belum lengkap.
- Pengelolaan material dan penggunaan produksi membutuhkan pengujian alur end-to-end.
- Beberapa modul terkait supplier/consignment bisa ditingkatkan dari sisi laporan dan approval.

---

## Phase 3 — Point of Sale, Barcode, dan Transaksi

Status: Selesai sebagian / sudah berjalan sesuai inti fitur

### Yang sudah selesai
- Barcode scanner API / input barcode sudah dirancang.
- Sistem identifikasi produk berdasarkan barcode dan variant aktif.
- Cart/session-based shopping cart telah dibuat.
- Checkout bisa menghasilkan transaksi dengan status `PENDING / UNPAID`.
- Metode pembayaran tersedia:
  - Cash
  - Bank Transfer
  - QRIS
- Pembayaran dapat diupload sebagai bukti.
- Sistem konfirmasi pembayaran akan mengubah status transaksi menjadi `COMPLETED / PAID`.
- Barang baru akan dipotong stok setelah pembayaran dikonfirmasi.
- Pencegahan overselling dengan `select_for_update()` dan pengecekan ketersediaan stok.
- Setiap perubahan stok tercatat di ledger.
- Flag `stock_deducted` dibuat untuk mencegah pengurangan stok ganda.
- Transaksi yang dibatalkan mengembalikan stok lewat movement return.
- Barcode label dapat diunduh dalam format PNG dan PDF.

### Detail implementasi
- Flow transaksi disusun agar stok tidak langsung berkurang saat checkout awal.
- Ini meminimalkan risiko double deduction dan menjaga konsistensi data.
- Transaksi penjualan diatur secara lebih aman dari sisi stock dan ledger.

### Yang belum selesai
- Pengujian end-to-end untuk flow scanner + checkout + payment confirmation.
- Validasi edge case saat stok habis atau pembeli mengubah jumlah pesanan.
- Perbaikan UI transaksi untuk pengalaman cashier lebih halus.
- Pembuatan log audit yang lebih lengkap untuk setiap perubahan status.

---

## Phase 4 — Pembayaran dan Invoice

Status: Selesai sebagian

### Yang sudah selesai
- Payment records dibuat dan dipisahkan dari status transaksi utama.
- Support partial payment / down payment / installment sudah direncanakan dan sebagian diimplementasikan.
- Transaksi dianggap `PAID` hanya jika total yang dibayarkan sesuai atau melebihi grand total.
- Sales invoice PDF sudah dibuat dengan branding Veloura.
- Invoice berisi itemized table dan detail total.

### Detail implementasi
- Pembayaran dan transaksi dibuat sebagai dua entitas yang terpisah agar lebih fleksibel untuk kasus pembayaran bertahap.
- Sistem menghitung status pembayaran secara independen dari status order.

### Yang belum selesai
- Pengujian penuh untuk payment status transition.
- Penanganan case refund dan failed payment lebih detail.
- Validasi invoice untuk berbagai skenario pembayaran (partial, overpayment, cancellation, refund).

---

## Phase 5 — Fitur Masa Depan / Coming Soon

Status: Sebagian model dan workflow sudah ada, tetapi implementasi dan integrasi UI belum lengkap.

### Yang masih direncanakan
- Pengelolaan pengukuran customer melalui UI.
- Pengelolaan fitting melalui UI.
- Business analytics dashboard dan laporan bisnis.
- Notifikasi in-app.
- Additional PDF reports.
- Integrasi workflow order, design, material, production, dan quality control.

### Detail
- Custom order, design, production, dan quality control sudah memiliki sebagian model, route, atau halaman; fitur-fitur tersebut tidak boleh dianggap belum dimulai, tetapi juga belum siap sebagai alur end-to-end.
- Status tombol dan statistik dashboard belum sepenuhnya mencerminkan implementasi backend yang ada.
- Temuan terverifikasi dan backlog perbaikan rinci dicatat pada bagian **Audit lanjutan dan backlog permasalahan** di akhir dokumen.

---

## Struktur Folder Proyek VELOURA Dashboard

Dokumen ini menjelaskan fungsi masing-masing folder dan file utama dalam proyek agar arsitektur aplikasi lebih mudah dipahami dan dikembangkan. Struktur dibuat mengikuti pendekatan Django modular, di mana setiap folder mewakili domain atau komponen tertentu dari sistem bisnis fashion management.

### 1) `config/` — konfigurasi inti proyek
Fungsi:
- Menyimpan setting utama aplikasi Django.
- Mengatur database, timezone, variable lingkungan, user model, static files, media files, dan URL global.
- Menjadi pusat konfigurasi agar semua app dapat berjalan dalam satu sistem terpadu.

File utama:
- `config/settings.py`  
  Berisi semua konfigurasi proyek, seperti:
  - `INSTALLED_APPS` untuk mendaftarkan aplikasi seperti `accounts`, `catalog`, `inventory`, `sales`, `payments`, dan lainnya.
  - koneksi database SQLite default atau MySQL/MariaDB jika dipakai di environment lain.
  - `AUTH_USER_MODEL = 'accounts.User'` agar user model custom dipakai seluruh aplikasi.
  - `STATIC_URL`, `STATICFILES_DIRS`, `MEDIA_URL`, `MEDIA_ROOT` untuk asset frontend dan file upload.
  - `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` untuk autentikasi.

- `config/urls.py`  
  Menjadi router utama proyek. Fungsi utamanya adalah mengarahkan URL global ke app tertentu, misalnya:
  - `''` ke `core.urls`
  - `'accounts/'` ke `accounts.urls`
  - `'catalog/'` ke `catalog.urls`
  - `'inventory/'` ke `inventory.urls`
  - `'sales/'` ke `sales.urls`
  dan seterusnya.

- `config/asgi.py` dan `config/wsgi.py`  
  Digunakan oleh server deployment atau runtime Django untuk menjalankan aplikasi.

Cara kerja:
- Saat server dijalankan, Django membaca `settings.py` untuk mengetahui konfigurasi.
- `urls.py` memetakan URL ke view yang tepat.
- Setiap app memiliki `urls.py` sendiri agar struktur tidak bercampur.

---

### 2) `core/` — pusat dashboard dan logika umum
Fungsi:
- Menyediakan halaman utama sistem.
- Mengatur dashboard per role.
- Menyimpan middleware dan mekanisme autentikasi/role-based redirect.
- Menjadi tempat bagi komponen yang bersifat umum di seluruh aplikasi.

File utama:
- `core/views.py`  
  Mengontrol view dashboard utama dan dashboard per role.

- `core/urls.py`  
  Menangani route seperti:
  - `/` → dashboard utama
  - `/health/` → cek kesehatan server
  - `/admin-dashboard/`
  - `/cashier-dashboard/`
  - `/designer-dashboard/`

- `core/middleware.py`  
  Biasanya dipakai untuk memeriksa role pengguna lalu mengarahkan ke dashboard yang sesuai.

- `core/context_processors.py`  
  Mengirim data konteks umum ke template, seperti role user, nama toko, atau variabel global aplikasi.

Cara kerja:
- Saat pengguna login, middleware/logic mengecek role mereka.
- User diarahkan ke dashboard yang sesuai dengan izin.
- Template umum dari `templates/base.html` dipakai di semua halaman, sehingga layout tetap konsisten.

---

### 3) `accounts/` — autentikasi, pengguna, dan peran
Fungsi:
- Mengatur login, logout, session, dan manajemen akun.
- Menyimpan model user custom.
- Menangani role-based access control.

File utama:
- `accounts/models.py`  
  Menyimpan model data user dan relasi role.

- `accounts/views.py`  
  Menangani halaman login, logout, dashboard personal, dan kemungkinan pengaturan akun.

- `accounts/urls.py`  
  Menghubungkan URL seperti login dan logout.

- `accounts/admin.py`  
  Mengatur tampilan model user di admin Django.

Cara kerja:
- User masuk ke halaman login.
- Django memvalidasi username dan password.
- Jika benar, session dibuat.
- Setelah login, user mendapatkan akses sesuai role seperti `ADMIN`, `CASHIER`, atau `DESIGNER`.

---

### 4) `customers/` — data pelanggan
Fungsi:
- Menyimpan profil pelanggan.
- Mengelola informasi kontak, data transaksi, dan riwayat pembelian.
- Menjadi dasar untuk fitur sales dan order.

Cara kerja:
- Pelanggan dibuat/diperbarui melalui admin atau form aplikasi.
- Saat order dibuat, data pelanggan dapat dihubungkan ke transaksi atau penjualan.
- Data pelanggan dipakai untuk histori pembelian, loyalitas, dan laporan.

---

### 5) `suppliers/` — data pemasok
Fungsi:
- Menyimpan informasi supplier atau vendor.
- Menghubungkan data supplier ke produk dan pembelian stok.

Cara kerja:
- Produk bisa memiliki supplier tertentu.
- Saat stok dibeli dari supplier, data supplier dipakai untuk pelacakan pembelian.
- Dengan data ini sistem dapat membangun histori pembelian dan laporan supplier.

---

### 6) `catalog/` — katalog produk
Fungsi:
- Menyimpan produk utama yang dijual.
- Mengatur detail produk, kategori, harga, stok, barcode, dan status.
- Menjadi pusat data produk yang ditampilkan ke pengguna.

File utama:
- `catalog/models.py`  
  Mencakup model seperti produk, variant, harga, barcode, dan status.

Cara kerja:
- Admin menambahkan produk baru.
- Produk disimpan di database dengan data seperti SKU, nama, supplier, status, harga, dan gambar.
- Ketika user membuka halaman katalog, data ini diambil lalu ditampilkan.
- Produk juga bisa dibedakan berdasarkan variant seperti ukuran, warna, dan barcode.

---

### 7) `inventory/` — pengelolaan stok dan persediaan
Fungsi:
- Mengatur barang masuk dan keluar.
- Menyimpan ledger stok untuk melihat perubahan historis.
- Memastikan data stok tetap konsisten.

Komponen penting:
- stock movement ledger
- purchase, sales, output, return, adjustment, damage/loss

Cara kerja:
- Setiap perubahan stok dicatat dengan waktu, user, alasan, jumlah sebelum/sesudah.
- Saat transaksi penjualan diproses, stok akan dicek terlebih dahulu.
- Jika terjadi pembatalan atau retur, stok bisa dikembalikan.
- Ini penting agar stok tidak berkurang dua kali atau tidak sesuai dengan transaksi.

---

### 8) `sales/` — transaksi penjualan
Fungsi:
- Menangani proses penjualan.
- Mengelola cart, checkout, dan transaksi akhir.
- Menghubungkan antara produk, pelanggan, pembayaran, dan stok.

Cara kerja:
- Cashier memilih produk dan memasukkannya ke keranjang.
- User memeriksa total pembelanjaan.
- Proses checkout membuat transaksi penjualan.
- Setelah pembayaran dikonfirmasi, status transaksi menjadi valid dan stok dapat dikurangi.
- Data penjualan kemudian dipakai untuk laporan, invoice, dan analisis.

---

### 9) `payments/` — pembayaran dan invoice
Fungsi:
- Menangani metode pembayaran.
- Menyimpan status pembayaran.
- Menangani bukti pembayaran.
- Mengatur invoice penjualan.

Metode pembayaran yang umum dipakai:
- Cash
- Bank Transfer
- QRIS

Cara kerja:
- Setelah sales checkout, status transaksi dibuat `PENDING` atau `UNPAID`.
- Pembeli membayar sesuai metode yang dipilih.
- Bukti pembayaran diupload dan diverifikasi.
- Ketika total sudah sesuai, status berubah menjadi `PAID` atau `COMPLETED`.
- Invoice dapat dibuat sesuai data transaksi dan pembayaran.

---

### 10) `orders/` — order management
Fungsi:
- Menyimpan order yang dibuat dari transaksi penjualan.
- Menjaga status order dari awal sampai selesai.
- Menjadi sumber data untuk tracking barang dan pembelian.

Cara kerja:
- Saat checkout, order dibuat.
- Order dapat berstatus pending, paid, completed, cancelled, atau status lain sesuai logika aplikasi.
- Data order dipakai untuk pelacakan status dan proses berikutnya seperti pengiriman, produksi, atau invoice.

---

### 11) `designs/` — desain produk dan rancangan kreatif
Fungsi:
- Menyimpan rancangan desain fashion.
- Mungkin digunakan untuk kebutuhan desain custom, koleksi, atau konten visual produk.

Cara kerja:
- Designer membuat konsep produk atau style tertentu.
- Desain disimpan dalam database dan bisa dikaitkan dengan katalog atau produksi.
- Selanjutnya data design bisa dipakai untuk proses pembuatan produk atau custom couture.

---

### 12) `production/` — proses pembuatan barang
Fungsi:
- Menangani workflow produksi.
- Mengelola bahan yang digunakan untuk membuat produk.
- Mencatat hasil produksi dari input materi menjadi barang jadi.

Cara kerja:
- Setelah desain atau order masuk, production memilih bahan dan proses kerja.
- Produksi mengurangi material dari inventory sesuai kebutuhan.
- Output produksi ditambahkan kembali sebagai stok siap jual atau siap kirim.
- Data ini membantu memastikan produksi sesuai dengan demand dan inventory tetap terjaga.

---

### 13) `documents/` — dokumen dan arsip sistem
Fungsi:
- Menyimpan dokumen pendukung operasional business.
- Mengelola laporan, surat, invoice, dokumen internal, dan file administratif.

Cara kerja:
- Dokumen bisa dibuat secara otomatis atau diupload oleh user.
- Dokumen dapat dihubungkan dengan transaksi atau aktivitas bisnis tertentu.
- File ini sering dipakai untuk arsip, keperluan audit, atau pelaporan.

---

### 14) `analytics/` — dashboard analisis bisnis
Fungsi:
- Menyediakan data statistik dan insight bisnis.
- Mengolah data dari sales, inventory, customer, dan payment.

Cara kerja:
- Sistem membaca data transaksi dan stok.
- Data diolah menjadi grafik, laporan, atau dashboard ringkas.
- Manajer atau admin dapat melihat performa bisnis, tren penjualan, dan kebutuhan stok.

---

### 15) `notifications/` — notifikasi aplikasi
Fungsi:
- Menyampaikan pesan atau pemberitahuan internal ke user.
- Dapat digunakan untuk reminder status transaksi, stok rendah, pembayaran, atau aktivitas penting.

Cara kerja:
- Event tertentu terjadi di sistem.
- Notification dibuat dan ditautkan ke user tertentu atau role tertentu.
- User dapat melihat status notifikasi di UI aplikasi.

---

### 16) `templates/` — folder tampilan halaman web
Fungsi:
- Menyimpan file HTML untuk seluruh UI aplikasi.
- Mengatur layout, halaman login, dashboard, error page, dan komponen umum.

File utama:
- `templates/base.html`  
  Template utama semua halaman. Di sini ada layout dari sidebar, topbar, content, dan blok `page_title`/`page_subtitle`.

- `templates/core/403.html`  
  Halaman khusus saat user tidak mempunyai izin akses. Ini biasanya menampilkan pesan "Access Denied".

Cara kerja:
- View Django memanggil template tertentu.
- Template menerima data dari view.
- Data disiapkan dan ditampilkan dalam bentuk HTML ke browser.

---

### 17) `static/` — file CSS, JavaScript, dan asset frontend
Fungsi:
- Menyimpan file frontend statis seperti CSS, JS, gambar, vendor library, dan icon.

Struktur umum:
- `static/css/`  
  Menyimpan stylesheet custom seperti `veloura.css`.

- `static/js/`  
  Menyimpan script JavaScript aplikasi seperti `veloura.js`.

- `static/vendor/`  
  Menyimpan library pihak ketiga seperti Bootstrap dan Lucide.

- `static/images/`  
  Menyimpan aset gambar.

Cara kerja:
- Django menghubungkan file statis melalui `STATIC_URL`.
- Browser meminta file CSS/JS tertentu saat halaman dimuat.
- CSS mengatur layout dan tampilan, JS mengatur logika interaksi dan animasi, dan gambar dipakai untuk branding atau elemen visual.

---

### 18) `manage.py` — file eksekusi utama Django
Fungsi:
- File utama yang dipakai untuk menjalankan server Django dan perintah CLI.

Contoh penggunaan:
- `python manage.py runserver`
- `python manage.py makemigrations`
- `python manage.py migrate`
- `python manage.py createsuperuser`

Cara kerja:
- File ini memanggil `django.core.management` dan menjalankan perintah sesuai kebutuhan.
- Tanpa `manage.py`, proyek Django tidak akan bisa dijalankan atau dikelola dari command line.

---

### 19) `db.sqlite3` — database lokal
Fungsi:
- Menyimpan data aplikasi dalam development environment.
- Database default yang dipakai saat proyek berjalan secara lokal.

Cara kerja:
- Saat migrasi dijalankan, tabel Django dibuat di SQLite.
- Data user, produk, stok, transaksi, dan order masuk ke database ini.
- Database ini umum dipakai untuk local development sebelum deploy ke environment production.

---

### 20) `progress.md` — dokumentasi status proyek
Fungsi:
- Menjadi catatan perkembangan proyek.
- Menjelaskan fase pengembangan, progress, dan pending item.

Cara kerja:
- Tim atau developer membaca file ini untuk melihat apa yang sudah selesai, apa yang masih dikerjakan, dan apa yang masih direncanakan.
- Ini membantu koordinasi dan menjaga akurasi proses pengembangan.

---

## Cara Kerja Keseluruhan Proyek Secara Sederhana

1. User mengakses URL tertentu.
2. Django membaca `config/urls.py` sebagai router utama.
3. Router mengarahkan request ke app yang sesuai (`accounts`, `sales`, `catalog`, dll).
4. App `views.py` memproses logic aplikasi.
5. Data diambil dari model dan database.
6. Data diproses dan dikirim ke template HTML.
7. Template menampilkan halaman yang dilihat user.
8. Saat terjadi transaksi, data dari berbagai module berkaitan satu sama lain, misalnya:
   - `catalog` untuk produk
   - `inventory` untuk stok
   - `sales` untuk transaksi
   - `payments` untuk pembayaran
   - `orders` untuk order tracking
   - `analytics` untuk laporan

Dengan pola seperti ini, proyek VELOURA menjadi modular dan mudah dikembangkan secara bertahap tanpa menggabungkan semua logika ke satu folder besar.

---

## Ringkasan Status Proyek

### Sudah selesai
- Fondasi proyek Django
- User role & auth
- Dashboard admin/cashier/designer (UI tersedia; angka ringkasan belum terhubung ke data)
- Katalog produk
- Variants dan barcode (terdapat kendala pada alur barcode yang dicatat pada hasil audit)
- Inventory + stock ledger
- POS dan pembuatan transaksi dasar
- Payment flow dasar (konfirmasi belum tersambung dari UI; lihat hasil audit)
- Invoice PDF dasar

### Masih perlu pengembangan
- Penyelesaian alur tailor/custom order dan production
- Penghubung UI ke seluruh aksi workflow yang tersedia
- Konsistensi status pembayaran, transaksi, stok, dan refund
- Analytics & report lanjutan
- Notifikasi in-app
- Pengujian otomatis; saat audit tidak ada test yang ditemukan berjalan
- Hardening keamanan dan edge-case validation

### Kesimpulan
Proyek VELOURA saat ini sudah berada di fase inti sistem bisnis fashion management, terutama pada area katalog, inventory, transaksi, dan pembayaran. Fokus utama selanjutnya adalah memperkuat validasi, pengujian, dan pengembangan modul lanjutan seperti custom order, produksi, dan analytics.

---

## Catatan tambahan
- Proyek menggunakan Django dengan SQLite untuk lokal development.
- Struktur siap untuk migrasi ke MariaDB/MySQL dalam waktu mendatang.
- Nilai uang menggunakan `DecimalField` untuk menjaga akurasi data.
- Data historis transaksi dipertahankan agar audit dan tracking tetap valid.

---
