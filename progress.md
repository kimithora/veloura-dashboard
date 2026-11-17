# Progress VELOURA Dashboard

**Pembaruan:** 17 November 2026  
**Status keseluruhan:** fitur dasar dan sebagian modul bisnis sudah tersedia, tetapi alur penjualan/pembayaran belum siap dianggap end-to-end atau teruji.  
**Catatan:** status fase mengacu pada kode yang diperiksa, bukan rencana awal. Temuan rinci dan urutan debugging ada di [audit.md](./audit.md).

## Ringkasan fase

| Fase | Status | Ringkasan |
|---|---|---|
| 0. Persiapan proyek | Selesai untuk pengembangan lokal | Project Django, app modular, SQLite, routing, template dasar tersedia. Deployment dan setup lintas mesin belum diverifikasi. |
| 1. Fondasi sistem | Sebagian selesai | Custom user, role, login, dashboard, dan pembatasan akses dasar tersedia. Cakupan test role dan akses tiap route belum ada. |
| 2. Katalog dan inventori | Sebagian selesai | Model katalog, varian, customer, supplier, material, serta ledger tersedia. Beberapa perubahan stok dapat melewati ledger; validasi dan concurrency perlu dibenahi. |
| 3. POS dan transaksi | Belum selesai / perlu debugging | Scanner, cart, checkout, dan detail transaksi tersedia. Checkout POS belum membuat pembayaran, validasi cart belum cukup, dan pembatalan transaksi belum tersambung dari UI. |
| 4. Pembayaran dan invoice | Sebagian selesai | Record pembayaran, konfirmasi, refund, dan invoice tersedia, termasuk UI konfirmasi dari daftar/detail transaksi. Refund menyelaraskan stok, bahkan pada transaksi multi-pembayaran. Belum ada tes otomatis. |
| 5. Custom order, desain, produksi | Sebagian selesai | Model, route/form/halaman workflow tersedia, termasuk UI CRUD Measurement dan Fitting yang sebelumnya placeholder. Validasi penugasan, snapshot desain, QC, material, dan sinkronisasi status masih perlu diperbaiki. |
| 6. Analytics dan fitur pendukung | Belum selesai | Analytics, notifications, documents, measurement, fitting, dan beberapa laporan/UI masih placeholder atau belum tersedia. |

## Fase 0 — Persiapan proyek

### Sudah tersedia
- Project Django dengan app modular dan konfigurasi database SQLite untuk pengembangan.
- Routing utama, template dasar, serta asset frontend.

### Masih perlu
- Verifikasi setup pada mesin baru dan dokumentasi instalasi yang konsisten.
- Manifest dependency agar lingkungan dapat direproduksi.
- Konfigurasi deployment dengan secret, `DEBUG`, dan host production yang eksplisit.

## Fase 1 — Fondasi sistem

### Sudah tersedia
- Custom user dan role ADMIN, CASHIER, DESIGNER.
- Login/logout serta dashboard berbasis role.
- Pembatasan role backend pada banyak view.

### Masih perlu
- Test otomatis untuk role yang diizinkan/ditolak.
- Pemeriksaan batas data berdasarkan penugasan designer di seluruh endpoint terkait.

## Fase 2 — Katalog dan inventori

### Sudah tersedia
- Produk, varian, barcode, customer, supplier, material, dan stock movement.
- Form dasar untuk sebagian besar pengelolaan katalog/inventori.

### Masih perlu
- Pastikan semua perubahan stok membuat ledger yang sesuai.
- Validasi jumlah dan stok pada semua jalur transaksi.
- Lindungi update stok material dari race condition dengan penguncian baris yang sesuai.
- Sinkronkan perubahan barcode varian dengan registry barcode.

## Fase 3 — POS dan transaksi

### Sudah tersedia
- Scanner/lookup barcode, session cart, checkout transaksi pending, detail transaksi, dan invoice.

### Belum selesai
- Checkout belum menyimpan pembayaran yang dipilih pada modal POS.
- Input kuantitas cart dan pemilihan customer belum berfungsi lengkap.
- Validasi backend untuk jumlah cart belum memadai.
- Tombol pembatalan belum terhubung ke service pembatalan.

### Langkah berikutnya
- Utamakan penyambungan checkout → Payment → konfirmasi → pemotongan stok dan ledger.
- Tambahkan tes alur sukses, pembayaran parsial, stok tidak cukup, pembatalan, dan request duplikat.

## Fase 4 — Pembayaran dan invoice

### Sudah tersedia
- Model dan form pencatatan pembayaran, endpoint konfirmasi/refund, UI konfirmasi/void dari daftar dan detail transaksi, template daftar pembayaran per transaksi, serta invoice PDF.
- Refund mengembalikan stok dan menyelaraskan status transaksi, termasuk skenario transaksi dengan beberapa pembayaran.

### Belum selesai
- Belum ada test untuk status pembayaran, pembayaran parsial, dan concurrency.

## Fase 5 — Custom order, desain, dan produksi

### Sudah tersedia
- Model dan sebagian halaman/route untuk order, desain, produksi, request material, pemakaian material, serta QC.
- Form custom barcode tersedia dari halaman detail produk.

### Belum selesai
- Pembatasan record berdasarkan penugasan designer belum merata.
- Nomor versi desain belum bertambah pada snapshot berikutnya.
- QC belum mensyaratkan semua checklist lolos sebelum Passed.
- Fulfill material request belum memperbarui persediaan.
- Status produksi/order dan histori perubahan belum selalu sinkron.

## Fase 6 — Analytics dan fitur pendukung

### Status
- Analytics, notifications, dan documents masih placeholder.
- Measurement dan fitting sekarang memiliki UI CRUD lengkap (daftar dan tambah data; nama customer/order ditampilkan via dot-notation filter).
- AJAX form di halaman detail (produksi, desain, order, pembayaran) sudah punya error handling (.catch) dan loading overlay, tidak lagi stuck saat submit.
- Statistik dashboard, pencarian global, beberapa tautan profil, dan laporan masih perlu implementasi.

## Pemeriksaan terakhir

- Django system check: **lolos**.
- Pemeriksaan migrasi: **tidak ada perubahan tertunda**.
- Django test runner: **0 test ditemukan**.
- Belum dilakukan pengujian end-to-end melalui browser atau database production.

## Prioritas kerja berikutnya

1. Selesaikan alur POS dan pembayaran beserta tes regresinya.
2. Selaraskan refund/pembatalan dengan stok dan ledger.
3. Perbaiki akses berbasis penugasan dan concurrency inventori.
4. Lengkapi workflow desain/produksi serta hilangkan placeholder UI yang menghambat.
5. Perbarui README, dependency, dan konfigurasi deployment setelah perilaku aplikasi stabil.
