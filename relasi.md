# Relasi Antar Entitas

**Pembaruan:** 19 November 2026 — menambah relasi `ORDER_PAYMENT` (pembayaran custom order) dan menyesuaikan penomoran.

## Keterangan Kardinalitas

- **1 : N** — Satu entitas dapat berhubungan dengan banyak entitas lain.
- **N : 1** — Banyak entitas berhubungan dengan satu entitas.
- **M : N** — Banyak entitas dapat berhubungan dengan banyak entitas lain.
- **Self-Relationship** — Relasi suatu entitas dengan entitasnya sendiri.

## 1. Relasi akses dan pengguna (Accounts)

| No. | Entitas pertama | Entitas kedua | Kardinalitas | Penjelasan relasi |
| --- | --- | --- | --- | --- |
| 1 | ROLE | USER | 1 : N | Satu role dapat dimiliki oleh banyak pengguna. Setiap pengguna memiliki satu role sebagai dasar pengaturan hak akses sistem. |
| 2 | USER | CUSTOMER | 1 : N | Satu pengguna dapat memiliki beberapa profil pelanggan yang terhubung dengannya. Hubungan ini bersifat opsional pada profil pelanggan. |
| 3 | USER | ORDER | 1 : N | Satu pengguna dapat membuat banyak pesanan sebagai kasir atau ditunjuk sebagai desainer. |
| 4 | USER | ORDER_STATUS_HISTORY | 1 : N | Satu pengguna dapat melakukan perubahan status pada banyak pesanan dan setiap perubahan dicatat dalam riwayat status. |
| 5 | USER | PAYMENT | 1 : N | Satu pengguna dapat mengonfirmasi banyak pembayaran sebagai petugas yang bertanggung jawab. |
| 6 | USER | ORDER_PAYMENT | 1 : N | Satu pengguna dapat mengonfirmasi banyak pembayaran custom order (DP/cicilan/lunas) sebagai petugas yang bertanggung jawab. |
| 7 | USER | PRODUCTION | 1 : N | Satu pengguna dapat bertanggung jawab sebagai desainer pada banyak proses produksi. |
| 8 | USER | MATERIAL_REQUEST | 1 : N | Satu pengguna dapat mengajukan maupun menyetujui banyak permintaan bahan baku. |
| 9 | USER | MATERIAL_USAGE | 1 : N | Satu pengguna dapat mencatat banyak aktivitas penggunaan bahan baku. |
| 10 | USER | QUALITY_CONTROL | 1 : N | Satu pengguna dapat melakukan pemeriksaan kualitas terhadap banyak hasil produksi. |
| 11 | USER | DESIGN | 1 : N | Satu pengguna dapat membuat banyak desain produk. |
| 12 | USER | DESIGN_VERSION | 1 : N | Satu pengguna dapat membuat banyak revisi atau versi desain. |
| 13 | USER | STOCK_MOVEMENT | 1 : N | Satu pengguna dapat mencatat banyak aktivitas pergerakan stok inventaris. |
| 14 | USER | TRANSACTION | 1 : N | Satu pengguna dapat melayani banyak transaksi penjualan sebagai kasir. |

## 2. Relasi pelanggan (Customers)

| No. | Entitas pertama | Entitas kedua | Kardinalitas | Penjelasan relasi |
| --- | --- | --- | --- | --- |
| 15 | CUSTOMER | ORDER | 1 : N | Satu pelanggan dapat melakukan banyak pemesanan produk atau layanan Veloura. |
| 16 | CUSTOMER | MEASUREMENT | 1 : N | Satu pelanggan dapat memiliki banyak catatan pengukuran ukuran tubuh untuk kebutuhan pembuatan pakaian. |
| 17 | CUSTOMER | FITTING | 1 : N | Satu pelanggan dapat mengikuti beberapa sesi fitting untuk memastikan kesesuaian pakaian. |
| 18 | CUSTOMER | TRANSACTION | 1 : N | Satu pelanggan dapat melakukan banyak transaksi pembelian. |

## 3. Relasi pesanan (Orders)

| No. | Entitas pertama | Entitas kedua | Kardinalitas | Penjelasan relasi |
| --- | --- | --- | --- | --- |
| 19 | ORDER | ORDER_STATUS_HISTORY | 1 : N | Satu pesanan dapat memiliki banyak catatan perubahan status untuk mendokumentasikan perkembangan pesanan. |
| 20 | ORDER | PRODUCTION | 1 : N | Satu pesanan dapat memiliki beberapa catatan proses produksi untuk memantau pengerjaannya. |
| 21 | ORDER | DESIGN | 1 : N | Satu pesanan dapat memiliki beberapa desain yang berkaitan dengan kebutuhan pelanggan. |
| 22 | ORDER | FITTING | 1 : N | Satu pesanan dapat memiliki beberapa jadwal atau sesi fitting. |
| 23 | ORDER | QUALITY_CONTROL | 1 : N | Satu pesanan dapat memiliki beberapa catatan pemeriksaan kualitas sebelum produk diserahkan kepada pelanggan. |
| 24 | ORDER | MEASUREMENT | 1 : N | Satu pesanan dapat dikaitkan dengan beberapa catatan pengukuran tubuh pelanggan sebagai referensi pengerjaan pakaian. |

## 4. Relasi katalog produk (Catalog)

| No. | Entitas pertama | Entitas kedua | Kardinalitas | Penjelasan relasi |
| --- | --- | --- | --- | --- |
| 25 | CATEGORY | PRODUCT | 1 : N | Satu kategori dapat mengelompokkan banyak produk berdasarkan jenis atau klasifikasi produk. |
| 26 | BRAND | PRODUCT | 1 : N | Satu merek dapat digunakan oleh banyak produk. Penggunaan merek pada produk bersifat opsional. |
| 27 | SUPPLIER | PRODUCT | 1 : N | Satu pemasok dapat memasok banyak produk. Hubungan pemasok dengan produk bersifat opsional. |
| 28 | PRODUCT | PRODUCT_VARIANT | 1 : N | Satu produk dapat memiliki banyak varian berdasarkan ukuran, warna, atau karakteristik lainnya. |
| 29 | PRODUCT_VARIANT | BARCODE | 1 : N | Satu varian produk dapat memiliki beberapa kode batang untuk keperluan identifikasi produk. |
| 30 | PRODUCT_VARIANT | TRANSACTION_ITEM | 1 : N | Satu varian produk dapat tercatat dalam banyak item transaksi penjualan. |
| 31 | BARCODE | BARCODE | Self-Relationship (1 : N) | Satu barcode dapat menjadi sumber bagi beberapa barcode baru yang dihasilkan melalui proses regenerasi kode batang. |

## 5. Relasi pemasok (Suppliers)

| No. | Entitas pertama | Entitas kedua | Kardinalitas | Penjelasan relasi |
| --- | --- | --- | --- | --- |
| 32 | SUPPLIER | MATERIAL | 1 : N | Satu pemasok dapat menyediakan berbagai jenis bahan baku yang digunakan dalam kegiatan produksi Veloura. Hubungan pemasok dengan bahan baku bersifat opsional. |

## 6. Relasi transaksi dan pembayaran (Sales & Payments)

| No. | Entitas pertama | Entitas kedua | Kardinalitas | Penjelasan relasi |
| --- | --- | --- | --- | --- |
| 33 | TRANSACTION | PAYMENT | 1 : N | Satu transaksi dapat memiliki beberapa catatan pembayaran, misalnya pembayaran uang muka dan pelunasan. |
| 34 | TRANSACTION | TRANSACTION_ITEM | 1 : N | Satu transaksi dapat terdiri atas banyak item produk yang dibeli pelanggan. |
| 35 | ORDER | ORDER_PAYMENT | 1 : N | Satu custom order dapat memiliki beberapa pembayaran (DP, cicilan, atau pelunasan). Setiap konfirmasi/void menyesuaikan `dp_amount` pada pesanan. |

## 7. Relasi inventaris (Inventory)

| No. | Entitas pertama | Entitas kedua | Kardinalitas | Penjelasan relasi |
| --- | --- | --- | --- | --- |
| 36 | MATERIAL | MATERIAL_REQUEST | 1 : N | Satu jenis bahan baku dapat muncul dalam banyak permintaan bahan untuk kebutuhan produksi. |
| 37 | MATERIAL | MATERIAL_USAGE | 1 : N | Satu jenis bahan baku dapat digunakan dalam banyak aktivitas produksi dan setiap penggunaannya dicatat. |
| 38 | DJANGO_CONTENT_TYPE | STOCK_MOVEMENT | 1 : N | Satu tipe konten Django dapat digunakan oleh banyak catatan pergerakan stok untuk mengidentifikasi jenis objek yang mengalami perubahan stok. |
| 39 | PRODUCT_VARIANT | STOCK_MOVEMENT | M : N | Varian produk dapat memiliki banyak catatan pergerakan stok, sedangkan mekanisme pencatatan stok menggunakan relasi polimorfik melalui ContentType. |
| 40 | MATERIAL | STOCK_MOVEMENT | M : N | Bahan baku dapat memiliki banyak catatan pergerakan stok melalui mekanisme Generic Foreign Key Django. |

## 8. Relasi produksi (Production)

| No. | Entitas pertama | Entitas kedua | Kardinalitas | Penjelasan relasi |
| --- | --- | --- | --- | --- |
| 41 | PRODUCTION | MATERIAL_REQUEST | 1 : N | Satu proses produksi dapat memiliki banyak permintaan bahan baku sesuai kebutuhan pengerjaan produk. |
| 42 | PRODUCTION | MATERIAL_USAGE | 1 : N | Satu proses produksi dapat memiliki banyak catatan penggunaan bahan baku selama proses pengerjaan. |
| 43 | MATERIAL_REQUEST | MATERIAL_USAGE | 1 : N | Satu permintaan bahan baku dapat direalisasikan melalui beberapa catatan penggunaan bahan selama produksi berlangsung. |

## Rekapitulasi seluruh relasi

| Kelompok relasi | Jumlah relasi |
| --- | ---: |
| Akses dan pengguna | 14 |
| Pelanggan | 4 |
| Pesanan | 6 |
| Katalog produk | 7 |
| Pemasok | 1 |
| Transaksi dan pembayaran | 3 |
| Inventaris | 5 |
| Produksi | 3 |
| **Total** | **43** |
