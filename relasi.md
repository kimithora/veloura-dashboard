# Relasi Antar Entitas

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
| 6 | USER | PRODUCTION | 1 : N | Satu pengguna dapat bertanggung jawab sebagai desainer pada banyak proses produksi. |
| 7 | USER | MATERIAL_REQUEST | 1 : N | Satu pengguna dapat mengajukan maupun menyetujui banyak permintaan bahan baku. |
| 8 | USER | MATERIAL_USAGE | 1 : N | Satu pengguna dapat mencatat banyak aktivitas penggunaan bahan baku. |
| 9 | USER | QUALITY_CONTROL | 1 : N | Satu pengguna dapat melakukan pemeriksaan kualitas terhadap banyak hasil produksi. |
| 10 | USER | DESIGN | 1 : N | Satu pengguna dapat membuat banyak desain produk. |
| 11 | USER | DESIGN_VERSION | 1 : N | Satu pengguna dapat membuat banyak revisi atau versi desain. |
| 12 | USER | STOCK_MOVEMENT | 1 : N | Satu pengguna dapat mencatat banyak aktivitas pergerakan stok inventaris. |
| 13 | USER | TRANSACTION | 1 : N | Satu pengguna dapat melayani banyak transaksi penjualan sebagai kasir. |

## 2. Relasi pelanggan (Customers)

| No. | Entitas pertama | Entitas kedua | Kardinalitas | Penjelasan relasi |
| --- | --- | --- | --- | --- |
| 14 | CUSTOMER | ORDER | 1 : N | Satu pelanggan dapat melakukan banyak pemesanan produk atau layanan Veloura. |
| 15 | CUSTOMER | MEASUREMENT | 1 : N | Satu pelanggan dapat memiliki banyak catatan pengukuran ukuran tubuh untuk kebutuhan pembuatan pakaian. |
| 16 | CUSTOMER | FITTING | 1 : N | Satu pelanggan dapat mengikuti beberapa sesi fitting untuk memastikan kesesuaian pakaian. |
| 17 | CUSTOMER | TRANSACTION | 1 : N | Satu pelanggan dapat melakukan banyak transaksi pembelian. |

## 3. Relasi pesanan (Orders)

| No. | Entitas pertama | Entitas kedua | Kardinalitas | Penjelasan relasi |
| --- | --- | --- | --- | --- |
| 18 | ORDER | ORDER_STATUS_HISTORY | 1 : N | Satu pesanan dapat memiliki banyak catatan perubahan status untuk mendokumentasikan perkembangan pesanan. |
| 19 | ORDER | PRODUCTION | 1 : N | Satu pesanan dapat memiliki beberapa catatan proses produksi untuk memantau pengerjaannya. |
| 20 | ORDER | DESIGN | 1 : N | Satu pesanan dapat memiliki beberapa desain yang berkaitan dengan kebutuhan pelanggan. |
| 21 | ORDER | FITTING | 1 : N | Satu pesanan dapat memiliki beberapa jadwal atau sesi fitting. |
| 22 | ORDER | QUALITY_CONTROL | 1 : N | Satu pesanan dapat memiliki beberapa catatan pemeriksaan kualitas sebelum produk diserahkan kepada pelanggan. |
| 23 | ORDER | MEASUREMENT | 1 : N | Satu pesanan dapat dikaitkan dengan beberapa catatan pengukuran tubuh pelanggan sebagai referensi pengerjaan pakaian. |

## 4. Relasi katalog produk (Catalog)

| No. | Entitas pertama | Entitas kedua | Kardinalitas | Penjelasan relasi |
| --- | --- | --- | --- | --- |
| 24 | CATEGORY | PRODUCT | 1 : N | Satu kategori dapat mengelompokkan banyak produk berdasarkan jenis atau klasifikasi produk. |
| 25 | BRAND | PRODUCT | 1 : N | Satu merek dapat digunakan oleh banyak produk. Penggunaan merek pada produk bersifat opsional. |
| 26 | SUPPLIER | PRODUCT | 1 : N | Satu pemasok dapat memasok banyak produk. Hubungan pemasok dengan produk bersifat opsional. |
| 27 | PRODUCT | PRODUCT_VARIANT | 1 : N | Satu produk dapat memiliki banyak varian berdasarkan ukuran, warna, atau karakteristik lainnya. |
| 28 | PRODUCT_VARIANT | BARCODE | 1 : N | Satu varian produk dapat memiliki beberapa kode batang untuk keperluan identifikasi produk. |
| 29 | PRODUCT_VARIANT | TRANSACTION_ITEM | 1 : N | Satu varian produk dapat tercatat dalam banyak item transaksi penjualan. |
| 30 | BARCODE | BARCODE | Self-Relationship (1 : N) | Satu barcode dapat menjadi sumber bagi beberapa barcode baru yang dihasilkan melalui proses regenerasi kode batang. |

## 5. Relasi pemasok (Suppliers)

| No. | Entitas pertama | Entitas kedua | Kardinalitas | Penjelasan relasi |
| --- | --- | --- | --- | --- |
| 31 | SUPPLIER | MATERIAL | 1 : N | Satu pemasok dapat menyediakan berbagai jenis bahan baku yang digunakan dalam kegiatan produksi Veloura. Hubungan pemasok dengan bahan baku bersifat opsional. |

## 6. Relasi transaksi dan pembayaran (Sales & Payments)

| No. | Entitas pertama | Entitas kedua | Kardinalitas | Penjelasan relasi |
| --- | --- | --- | --- | --- |
| 32 | TRANSACTION | PAYMENT | 1 : N | Satu transaksi dapat memiliki beberapa catatan pembayaran, misalnya pembayaran uang muka dan pelunasan. |
| 33 | TRANSACTION | TRANSACTION_ITEM | 1 : N | Satu transaksi dapat terdiri atas banyak item produk yang dibeli pelanggan. |

## 7. Relasi inventaris (Inventory)

| No. | Entitas pertama | Entitas kedua | Kardinalitas | Penjelasan relasi |
| --- | --- | --- | --- | --- |
| 34 | MATERIAL | MATERIAL_REQUEST | 1 : N | Satu jenis bahan baku dapat muncul dalam banyak permintaan bahan untuk kebutuhan produksi. |
| 35 | MATERIAL | MATERIAL_USAGE | 1 : N | Satu jenis bahan baku dapat digunakan dalam banyak aktivitas produksi dan setiap penggunaannya dicatat. |
| 36 | DJANGO_CONTENT_TYPE | STOCK_MOVEMENT | 1 : N | Satu tipe konten Django dapat digunakan oleh banyak catatan pergerakan stok untuk mengidentifikasi jenis objek yang mengalami perubahan stok. |
| 37 | PRODUCT_VARIANT | STOCK_MOVEMENT | M : N | Varian produk dapat memiliki banyak catatan pergerakan stok, sedangkan mekanisme pencatatan stok menggunakan relasi polimorfik melalui ContentType. |
| 38 | MATERIAL | STOCK_MOVEMENT | M : N | Bahan baku dapat memiliki banyak catatan pergerakan stok melalui mekanisme Generic Foreign Key Django. |

## 8. Relasi produksi (Production)

| No. | Entitas pertama | Entitas kedua | Kardinalitas | Penjelasan relasi |
| --- | --- | --- | --- | --- |
| 39 | PRODUCTION | MATERIAL_REQUEST | 1 : N | Satu proses produksi dapat memiliki banyak permintaan bahan baku sesuai kebutuhan pengerjaan produk. |
| 40 | PRODUCTION | MATERIAL_USAGE | 1 : N | Satu proses produksi dapat memiliki banyak catatan penggunaan bahan baku selama proses pengerjaan. |
| 41 | MATERIAL_REQUEST | MATERIAL_USAGE | 1 : N | Satu permintaan bahan baku dapat direalisasikan melalui beberapa catatan penggunaan bahan selama produksi berlangsung. |

## Rekapitulasi seluruh relasi

| Kelompok relasi | Jumlah relasi |
| --- | ---: |
| Akses dan pengguna | 13 |
| Pelanggan | 4 |
| Pesanan | 6 |
| Katalog produk | 7 |
| Pemasok | 1 |
| Transaksi dan pembayaran | 2 |
| Inventaris | 5 |
| Produksi | 3 |
| **Total** | **41** |