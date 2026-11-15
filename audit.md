# Audit lanjutan dan backlog permasalahan

Tanggal audit: 15 November 2026  
Status: audit kode dan template; temuan di bawah belum diperbaiki kecuali dinyatakan lain. Daftar ini memuat masalah yang terverifikasi saat pemeriksaan, bukan klaim bahwa setiap kemungkinan bug sudah ditemukan.

## Prioritas P0 — menghambat atau merusak alur bisnis inti

- [ ] **POS tidak mencatat pembayaran yang dipilih.** Modal POS mengumpulkan metode pembayaran dan bukti, tetapi JavaScript hanya mengirim customer, diskon, dan notes ke endpoint checkout. Endpoint checkout hanya membuat transaksi `PENDING / UNPAID`; metode dan bukti pembayaran tidak disimpan sebagai `Payment`. Akibatnya tombol konfirmasi di POS tidak menjalankan transaksi pembayaran seperti labelnya.
- [ ] **Tidak ada aksi UI untuk mengonfirmasi pembayaran pending.** Endpoint konfirmasi tersedia, tetapi halaman detail dan daftar pembayaran hanya menyediakan detail/batal-refund. Pembayaran yang dicatat tidak dapat dikonfirmasi melalui alur UI yang ditemukan, sehingga status `PAID / COMPLETED` dan pengurangan stok tidak dapat diselesaikan dari aplikasi.
- [ ] **Refund pembayaran terkonfirmasi tidak memulihkan stok.** Refund mengubah status pembayaran dan menghitung ulang status transaksi, tetapi tidak memanggil pembatalan transaksi atau membuat movement pengembalian stok. Transaksi yang sebelumnya sudah memotong stok dapat menjadi pending/unpaid tanpa mengembalikan stok.
- [ ] **Halaman pembayaran per transaksi gagal dirender.** Route `payments:transaction_payments` memanggil template `payments/transaction_payments.html`, tetapi file template tidak tersedia; hasil verifikasi adalah `TemplateDoesNotExist`.
- [ ] **Tombol Cancel Transaction tidak membatalkan transaksi.** Tombol pada detail transaksi hanya memiliki `data-confirm`; tidak ada form, request, route, atau view pembatalan yang dipanggil darinya. Fungsi pembatalan di service tidak terhubung ke UI maupun route.
- [ ] **Form custom barcode gagal saat dibuka.** Pada GET form, `catalog.views.create_custom_barcode` memanggil `reverse('catalog:product_detail', pk=...)`; argumen `pk` harus diberikan melalui `kwargs`, sehingga pemanggilan tersebut melempar `TypeError`. Route juga tidak ditautkan dari halaman detail produk, dan pilihan `label_format` pada form belum digunakan untuk menentukan hasil.

## Prioritas P1 — workflow aktif belum tersambung atau berisiko menghasilkan data tidak konsisten

- [ ] **Perubahan jumlah item di POS tidak tersimpan.** Input kuantitas dan fungsi `changeQty` ada, tetapi tidak ada event listener yang memanggil fungsi tersebut saat nilai input berubah.
- [ ] **Tabel keranjang POS tidak sejajar dengan header.** Header memiliki tujuh kolom, sedangkan setiap baris item hanya menghasilkan enam sel; informasi ukuran/warna ditempatkan bersama nama produk dan kolom berikutnya bergeser.
- [ ] **Pilihan customer POS tidak berfungsi.** Dropdown hanya berisi walk-in; view tidak mengirim daftar customer dan tidak ada script untuk mengisinya.
- [ ] **Nilai stok dan jumlah keranjang belum divalidasi pada saat penambahan.** Endpoint cart menerima angka quantity tanpa guard untuk input bukan angka atau nilai nol/negatif dan tidak mengecek jumlah terhadap stok saat itu. Pemeriksaan kekurangan stok baru terjadi saat konfirmasi pembayaran.
- [ ] **Pembatalan/refund parsial belum menjaga status transaksi dengan benar.** Penanganan refund hanya menghitung ulang total pembayaran; tidak memperhitungkan bahwa stok mungkin sudah dipotong untuk transaksi yang telah lunas.
- [ ] **Versi desain dapat gagal pada perubahan status berikutnya.** Setiap perubahan status membuat `DesignVersion` dengan `version_number=design.version`, tetapi nomor versi desain tidak dinaikkan. Karena pasangan desain/nomor versi unik, perubahan berikutnya dapat menimbulkan `IntegrityError`.
- [ ] **Aksi barcode regenerasi tidak tersedia dari daftar barcode.** Endpoint regenerasi ada, tetapi daftar barcode tidak menyajikan tombol regenerasi. Route regenerasi menerima GET dan mengubah data, bukan membatasi perubahan ke POST.
- [ ] **Riwayat barcode dapat berbeda dari barcode varian.** Form edit varian mengubah `ProductVariant.barcode` tanpa menyinkronkan record `Barcode`; POS mencari berdasarkan barcode varian sementara daftar/label bekerja dengan registry barcode. Ini dapat menghasilkan daftar lama atau label yang tidak sesuai dengan record yang dipilih.
- [ ] **Stok varian dapat diubah tanpa ledger.** Form edit `ProductVariant` mengekspos `stock_quantity`, sehingga nilai stok dapat diubah langsung tanpa membuat `StockMovement`.
- [ ] **Penyesuaian stok material rentan kehilangan update bersamaan.** Nilai stok awal dibaca sebelum transaksi atomik dan row tidak dikunci sebelum dihitung lalu disimpan; update bersamaan dapat menimpa satu sama lain.
- [ ] **Pencatatan pemakaian material memiliki risiko race serupa.** Stok material dibaca sebelum transaksi atomik dan tidak dikunci dengan `select_for_update()` sebelum pengurangan.
- [ ] **Fulfill permintaan material tidak mengubah persediaan.** Aksi hanya mengubah status request; tidak mengurangi stok, membuat catatan usage, atau membuat stock movement. Tidak ada kontrol transisi status, sehingga permintaan dapat langsung ditandai fulfilled tanpa alur approval.
- [ ] **Aksi request material belum tersedia di UI.** Endpoint approve/fulfill/reject ada, tetapi daftar memakai template generik tanpa tombol yang memanggil endpoint. Tombol “Record Usage” di detail produksi masih berupa tautan `#`, meskipun form dan route pencatatan usage tersedia.
- [ ] **QC dapat ditandai Passed tanpa semua checklist lolos.** Model menyediakan `all_checks_passed`, tetapi pembuatan QC tidak menegakkan syarat itu sebelum menerima status `PASSED`.
- [ ] **Update status produksi/order/desain tidak selalu terhubung ke state lain.** Penyelesaian produksi tidak memperbarui status order secara otomatis; update order langsung lewat form dapat melewati pencatatan `OrderStatusHistory`.

## Prioritas P1 — pembatasan akses belum konsisten

- [ ] **Designer dapat mengedit order yang tidak ditugaskan kepadanya.** `OrderUpdateView` mengizinkan role designer tetapi queryset tidak dibatasi ke order milik designer tersebut; form juga mencakup status, customer, dan designer.
- [ ] **Endpoint perubahan status order tidak memeriksa penugasan designer.** Endpoint hanya memeriksa role, lalu mengambil order berdasarkan ID.
- [ ] **Endpoint update produksi tidak memeriksa penugasan designer.** Halaman detail membatasi produksi designer, tetapi endpoint POST hanya memeriksa role.
- [ ] **Endpoint update status desain tidak memeriksa penugasan designer.** Detail desain membatasi queryset, namun endpoint perubahan status hanya memeriksa role.
- [ ] **Aksi permintaan material tidak memeriksa hubungan designer dengan produksi/request.** Designer dapat mengirim aksi ke request berdasarkan ID tanpa pengecekan penugasan pada endpoint.
- [ ] **Form pencatatan pemakaian material tidak membatasi pilihan produksi, request, dan material berdasarkan penugasan maupun kecocokan satu sama lain.** Perlu validasi backend agar pemakaian tercatat pada produksi/request yang benar.
- [ ] **Endpoint hapus/bersihkan keranjang hanya memerlukan login.** `cart_remove` dan `cart_clear` tidak melakukan pemeriksaan role cashier/admin seperti POS, add, dan checkout. Perlu konsistensi kebijakan akses.

## Prioritas P2 — fitur ada sebagian tetapi belum dapat dipakai dari UI atau belum diimplementasikan

- [ ] **Measurement belum memiliki route/view/form aplikasi.** Model `customers.Measurement` tersedia, tetapi belum ada UI CRUD; tautan dashboard dan “Link Measurement” masih placeholder.
- [ ] **Fitting belum memiliki route/view/form aplikasi.** Model `production.Fitting` tersedia, tetapi tidak ada endpoint atau halaman pengelolaan; tautan dashboard masih placeholder.
- [ ] **Analytics, notifications, dan documents masih placeholder.** View masing-masing hanya mengembalikan halaman teks sederhana, belum memuat fungsi bisnis.
- [ ] **Statistik dashboard masih statis.** Angka ditampilkan sebagai `—`; view dashboard tidak mengirim hitungan pengguna, produk, penjualan, transaksi, atau stok rendah.
- [ ] **Global search belum memiliki alur pencarian.** Kolom search di topbar tidak berada dalam form dan tombolnya tidak menjalankan pencarian.
- [ ] **Tautan notifikasi dan profil di topbar belum berfungsi.** Keduanya masih menggunakan `href="#"`; fitur halaman profil juga belum tersedia.
- [ ] **Navigasi/teks dashboard belum mencerminkan keadaan fitur.** Dashboard designer memberi label coming soon pada order, design, dan production yang sudah memiliki sebagian halaman/route; dashboard admin menyatakan Phase 3 selesai padahal alur POS/pembayaran belum tersambung.
- [ ] **Beberapa tombol aksi masih placeholder meski modul terkait tersedia.** Termasuk Manage Design/Production dari order detail, Record Usage dari production detail, dan sebagian tautan laporan/invoice/dashboard.
- [ ] **Laporan penjualan belum berupa laporan.** Tautan “Sales Reports” mengarah ke daftar transaksi; tidak ditemukan agregasi/report penjualan. Label Invoices di dashboard kasir juga belum menaut ke daftar invoice.
- [ ] **Pembuatan custom barcode tidak dapat ditemukan dari halaman produk.** Route tersedia, tetapi halaman detail varian tidak menampilkan tautan ke form tersebut.
- [ ] **Pendaftaran publik memang ditolak oleh view.** Ini sesuai dengan komentar kebijakan admin-only, tetapi route `/accounts/register/` tetap ada dan perlu dipastikan dokumentasi/UI menyebutnya sebagai fitur nonaktif, bukan fitur registrasi yang siap digunakan.
- [ ] **Histori versi desain belum mencatat revisi edit secara lengkap.** Form edit desain tidak membuat snapshot versi; endpoint status membuat snapshot tetapi menggunakan nomor versi yang sama.
- [ ] **Pengelolaan pembelian/consignment belum menjadi alur inventory lengkap.** Supplier dan tipe produk ada, tetapi tidak ditemukan workflow penerimaan pembelian/settlement consignment yang menjaga stok serta ledger secara terintegrasi.

## Prioritas P2 — dokumentasi, konfigurasi, dan verifikasi

- [ ] **Semua app `tests.py` kosong/tidak memiliki test case.** `python manage.py test` melaporkan `Found 0 test(s)`, sehingga fitur tidak boleh disebut “tested” sebelum tes ditambahkan dan dijalankan.
- [ ] **README menyebut fitur “Working & Tested” dan fase custom order/production sebagai future, padahal kode saat ini berisi implementasi parsial.** Samakan README dengan status aktual serta bedakan model, endpoint, UI, dan alur end-to-end.
- [ ] **Instruksi seed README memakai heredoc Unix (`<< 'EOF'`) di bagian Quick Start Windows PowerShell.** Instruksi itu bukan sintaks PowerShell dan perlu diganti dengan langkah Windows yang dapat dijalankan.
- [ ] **Belum ada manifest dependency yang ditemukan di root.** Setup mengandalkan perintah instalasi manual; tambahkan dependency lock/manifest sebelum menargetkan instalasi konsisten lintas mesin.
- [ ] **Konfigurasi default belum aman untuk deployment.** `DEBUG` default aktif dan `SECRET_KEY` memiliki nilai development fallback; deployment harus mewajibkan secret/environment production dan konfigurasi host yang benar.
- [ ] **Pengujian role dan validasi akses seluruh route belum tersedia.** Perlu tes untuk role yang berhak/ditolak serta batas data antar-designer.
- [ ] **Kasus pembayaran, refund, overselling, race condition stok, transaksi diskon, dan perubahan status belum memiliki tes regresi.**

## Hasil pemeriksaan saat audit

- `python manage.py check`: lolos, tidak menemukan masalah konfigurasi Django.
- `python manage.py makemigrations --check --dry-run`: tidak ada perubahan migrasi yang tertunda.
- `python manage.py test`: 0 test ditemukan; ini bukan bukti alur bisnis berhasil.
- Verifikasi template menemukan `payments/transaction_payments.html` tidak tersedia.
- Verifikasi nama route pada tag `{% url %}` yang diperiksa tidak menemukan nama route yang hilang; ini tidak menjamin view/aksi tujuan bekerja.
