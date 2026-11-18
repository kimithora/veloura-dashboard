# ERD — VELOURA Fashion Management System

**Tanggal:** 19 November 2026  
**Sumber:** `db.sqlite3` (skema aktual)  
**Catatan:** dokumen ini menjelaskan seluruh relasi antar tabel di database VELOURA. Semua tipe data, primary key (PK), foreign key (FK), unique key (UK), dan index yang disebutkan mengacu pada DDL aktual di SQLite.  
**Status data:** database dikosongkan untuk presentasi demo pada 19 Nov 2026 — seluruh baris data bisnis dihapus, tersisa hanya user/role dan tabel framework. **Skema (DDL) tetap sama**, jadi dokumen ini tetap berlaku.

---

## Daftar Isi

1. [Legenda dan Konvensi](#1-legenda-dan-konvensi)
2. [Tabel Sistem Django](#2-tabel-sistem-django)
3. [Domain Akses dan Pengguna (Accounts)](#3-domain-akses-dan-pengguna-accounts)
4. [Domain Pelanggan (Customers)](#4-domain-pelanggan-customers)
5. [Domain Pesanan (Orders)](#5-domain-pesanan-orders)
6. [Domain Katalog (Catalog)](#6-domain-katalog-catalog)
7. [Domain Pemasok (Suppliers)](#7-domain-pemasok-suppliers)
8. [Domain Penjualan (Sales)](#8-domain-penjualan-sales)
9. [Domain Pembayaran (Payments)](#9-domain-pembayaran-payments)
10. [Domain Inventori (Inventory)](#10-domain-inventori-inventory)
11. [Domain Produksi (Production)](#11-domain-produksi-production)
12. [Domain Desain (Designs)](#12-domain-desain-designs)
13. [Relasi Polimorfik (ContentType)](#13-relasi-polimorfik-contenttype)
14. [Relasi Self-Reference (Barcode)](#14-relasi-self-reference-barcode)
15. [Relasi Audit (created_by / updated_by)](#15-relasi-audit-created_by--updated_by)
16. [Unique Constraint dan Index Penting](#16-unique-constraint-dan-index-penting)
17. [Ringkasan Kardinalitas](#17-ringkasan-kardinalitas)
18. [Alur Bisnis dan Relasinya](#18-alur-bisnis-dan-relasinya)

---

## 1. Legenda dan Konvensi

| Simbol | Arti |
|---|---|
| PK | Primary Key |
| FK | Foreign Key |
| UK | Unique Key |
| 1 : N | Satu entitas ke banyak entitas |
| N : 1 | Banyak entitas ke satu entitas |
| M : N | Banyak ke banyak (biasanya via junction/polymorphic) |
| 1 : 1 | Satu ke satu |

Konvensi penamaan kolom:
- Semua tabel bisnis memakai `id` integer primary key autoincrement.
- Kolom `created_at` dan `updated_at` ada di hampir semua tabel bisnis (dari `BaseModel`).
- Kolom `created_by_id` dan `updated_by_id` ada di tabel yang memakai `AuditMixin` (kebanyakan tabel bisnis, kecuali `TRANSACTION_ITEM`, `DJANGO_CONTENT_TYPE`, `BARCODE` tidak memakai AuditMixin).
- Foreign key Django biasanya `bigint` yang merujuk `integer id` tabel lain (SQLite fleksibel).
- `DEFERRABLE INITIALLY DEFERRED` pada FK SQLite artinya constraint FK baru diperiksa saat commit, bukan saat insert.

---

## 2. Tabel Sistem Django

Tabel-tabel ini dipakai Django untuk auth, admin, session, dan content type. Tidak didesain manual, tapi ikut dipakai oleh aplikasi.

| Tabel | Fungsi | Relasi Penting |
|---|---|---|
| `django_content_type` | Menyimpan tipe konten (`app_label`, `model`) untuk generic foreign key | `auth_permission`, `inventory_stockmovement`, `django_admin_log` |
| `django_migrations` | Mencatat migrasi yang sudah dijalankan | — |
| `django_session` | Menyimpan sesi login | `accounts_user` (tidak FK, tapi session_key dari user login) |
| `django_admin_log` | Log aksi di Django admin | `accounts_user`, `django_content_type` |
| `auth_group` | Grup izin Django | `auth_permission` |
| `auth_permission` | Izin per content type | `django_content_type`, `accounts_user`, `auth_group` |
| `auth_group_permissions` | Junction many-to-many GROUP ↔ PERMISSION | `auth_group`, `auth_permission` |
| `accounts_user_groups` | Junction many-to-many USER ↔ GROUP | `accounts_user`, `auth_group` |
| `accounts_user_user_permissions` | Junction many-to-many USER ↔ PERMISSION | `accounts_user`, `auth_permission` |

| Tabel | Kolom PK/UK | Kolom FK |
|---|---|---|
| `django_content_type` | `id` PK, `app_label`+`model` UK | — |
| `django_session` | `session_key` PK | — |
| `django_admin_log` | `id` PK | `content_type_id` FK → `django_content_type.id`, `user_id` FK → `accounts_user.id` |
| `auth_permission` | `id` PK, `content_type_id`+`codename` UK | `content_type_id` FK → `django_content_type.id` |
| `auth_group` | `id` PK, `name` UK | — |
| `auth_group_permissions` | `id` PK, `group_id`+`permission_id` UK | `group_id` FK → `auth_group.id`, `permission_id` FK → `auth_permission.id` |
| `accounts_user_groups` | `id` PK, `user_id`+`group_id` UK | `user_id` FK → `accounts_user.id`, `group_id` FK → `auth_group.id` |
| `accounts_user_user_permissions` | `id` PK, `user_id`+`permission_id` UK | `user_id` FK → `accounts_user.id`, `permission_id` FK → `auth_permission.id` |

---

## 3. Domain Akses dan Pengguna (Accounts)

### 3.1 ROLE

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `code` | varchar(20) | NOT NULL, UK |
| `name` | varchar(100) | NOT NULL |
| `description` | text | NOT NULL |

### 3.2 USER

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `password` | varchar(128) | NOT NULL |
| `last_login` | datetime | NULL |
| `is_superuser` | bool | NOT NULL |
| `username` | varchar(150) | NOT NULL, UK |
| `first_name` | varchar(150) | NOT NULL |
| `last_name` | varchar(150) | NOT NULL |
| `email` | varchar(254) | NOT NULL |
| `is_active` | bool | NOT NULL |
| `date_joined` | datetime | NOT NULL |
| `phone` | varchar(20) | NOT NULL |
| `address` | text | NOT NULL |
| `is_staff` | bool | NOT NULL |
| `role_id` | bigint | NULL, FK → `accounts_role.id` |

### 3.3 Relasi Accounts

| Dari | Ke | Kardinalitas | Keterangan |
|---|---|---|---|
| ROLE | USER | 1 : N | Satu role dimiliki banyak user. `role_id` nullable, jadi user bisa tanpa role (untuk superuser/admin default). |
| USER | CUSTOMER | 1 : N | Satu user bisa punya beberapa profil customer yang terhubung (`user_id` FK di customer, nullable). |
| USER | ORDER | 1 : N | Satu user berperan sebagai kasir pembuat (`cashier_id`) dan/atau desainer yang ditunjuk (`designer_id`). |
| USER | ORDER_STATUS_HISTORY | 1 : N | Satu user bisa melakukan banyak perubahan status order. |
| USER | PAYMENT | 1 : N | Satu user bisa mengonfirmasi banyak pembayaran (`confirmed_by_id`). |
| USER | ORDER_PAYMENT | 1 : N | Satu user bisa mengonfirmasi banyak pembayaran custom order (`confirmed_by_id`). |
| USER | PRODUCTION | 1 : N | Satu user ditunjuk sebagai desainer produksi (`designer_id`). |
| USER | MATERIAL_REQUEST | 1 : N | Satu user bisa mengajukan (`requested_by_id`) dan menyetujui (`approved_by_id`) banyak permintaan bahan. |
| USER | MATERIAL_USAGE | 1 : N | Satu user bisa mencatat banyak pemakaian bahan (`used_by_id`). |
| USER | QUALITY_CONTROL | 1 : N | Satu user bisa melakukan banyak pemeriksaan QC (`qc_by_id`). |
| USER | DESIGN | 1 : N | Satu user bisa membuat banyak desain (`designer_id`). |
| USER | DESIGN_VERSION | 1 : N | Satu user bisa membuat banyak revisi/desain version (`created_by_id`). |
| USER | STOCK_MOVEMENT | 1 : N | Satu user bisa mencatat banyak pergerakan stok. |
| USER | TRANSACTION | 1 : N | Satu user melayani banyak transaksi penjualan sebagai kasir. |
| USER | DJANGO_ADMIN_LOG | 1 : N | Satu user bisa punya banyak log admin. |

---

## 4. Domain Pelanggan (Customers)

### 4.1 CUSTOMER

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `customer_id` | varchar(32) | NOT NULL, UK, index |
| `full_name` | varchar(150) | NOT NULL |
| `phone` | varchar(32) | NOT NULL, index |
| `email` | varchar(254) | NOT NULL, index |
| `address` | text | NOT NULL |
| `notes` | text | NOT NULL |
| `source` | varchar(16) | NOT NULL |
| `total_spending` | decimal | NOT NULL |
| `user_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `created_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `updated_by_id` | bigint | NULL, FK → `accounts_user.id`, index |

### 4.2 MEASUREMENT

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `measurement_id` | varchar(32) | NOT NULL, UK, index |
| `measurement_date` | date | NOT NULL |
| `chest_circumference` | decimal | NOT NULL |
| `waist_circumference` | decimal | NOT NULL |
| `hip_circumference` | decimal | NOT NULL |
| `shoulder_width` | decimal | NOT NULL |
| `sleeve_length` | decimal | NOT NULL |
| `arm_circumference` | decimal | NOT NULL |
| `neck_circumference` | decimal | NOT NULL |
| `garment_length` | decimal | NOT NULL |
| `skirt_trouser_length` | decimal | NOT NULL |
| `notes` | text | NOT NULL |
| `customer_id` | bigint | NOT NULL, FK → `customers_customer.id`, index |
| `order_id` | bigint | NULL, FK → `orders_order.id`, index |
| `created_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `updated_by_id` | bigint | NULL, FK → `accounts_user.id`, index |

### 4.3 Relasi Customers

| Dari | Ke | Kardinalitas | Keterangan |
|---|---|---|---|
| CUSTOMER | MEASUREMENT | 1 : N | Satu customer bisa punya banyak catatan ukuran badan. |
| CUSTOMER | ORDER | 1 : N | Satu customer bisa memesan banyak custom order. |
| CUSTOMER | FITTING | 1 : N | Satu customer bisa mengikuti banyak sesi fitting. |
| CUSTOMER | TRANSACTION | 1 : N | Satu customer bisa bertransaksi banyak kali di POS. |
| MEASUREMENT | ORDER | N : 1 | Banyak measurement bisa dikaitkan ke satu order (opsional). |

---

## 5. Domain Pesanan (Orders)

### 5.1 ORDER

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `order_number` | varchar(64) | NOT NULL, UK, index |
| `status` | varchar(20) | NOT NULL, index |
| `order_date` | datetime | NOT NULL, index |
| `required_date` | date | NULL |
| `description` | text | NOT NULL |
| `total_amount` | decimal | NOT NULL |
| `dp_amount` | decimal | NOT NULL |
| `notes` | text | NOT NULL |
| `customer_id` | bigint | NOT NULL, FK → `customers_customer.id`, index |
| `cashier_id` | bigint | NOT NULL, FK → `accounts_user.id`, index |
| `designer_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `created_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `updated_by_id` | bigint | NULL, FK → `accounts_user.id`, index |

### 5.2 ORDER_STATUS_HISTORY

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `status` | varchar(20) | NOT NULL |
| `changed_at` | datetime | NOT NULL, index |
| `notes` | text | NOT NULL |
| `order_id` | bigint | NOT NULL, FK → `orders_order.id`, index |
| `changed_by_id` | bigint | NULL, FK → `accounts_user.id`, index |

### 5.3 Relasi Orders

| Dari | Ke | Kardinalitas | Keterangan |
|---|---|---|---|
| ORDER | ORDER_STATUS_HISTORY | 1 : N | Satu order punya banyak catatan perubahan status. |
| ORDER | PRODUCTION | 1 : N | Satu order bisa punya banyak rekam produksi. |
| ORDER | DESIGN | 1 : N | Satu order bisa punya banyak desain. |
| ORDER | FITTING | 1 : N | Satu order bisa punya banyak sesi fitting. |
| ORDER | QUALITY_CONTROL | 1 : N | Satu order bisa punya banyak catatan QC. |
| ORDER | MEASUREMENT | 1 : N | Satu order bisa dikaitkan banyak measurement (opsional). |
| ORDER | CUSTOMER | N : 1 | Banyak order dimiliki satu customer. |
| ORDER | USER (cashier) | N : 1 | Banyak order dibuat oleh satu kasir. |
| ORDER | USER (designer) | N : 1 | Banyak order ditunjuk ke satu desainer (nullable). |

---

## 6. Domain Katalog (Catalog)

### 6.1 CATEGORY

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `name` | varchar(100) | NOT NULL, UK |
| `slug` | varchar(100) | NOT NULL, UK |
| `description` | text | NOT NULL |

### 6.2 BRAND

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `name` | varchar(100) | NOT NULL, UK |
| `slug` | varchar(100) | NOT NULL, UK |
| `description` | text | NOT NULL |

### 6.3 PRODUCT

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `sku` | varchar(64) | NOT NULL, UK, index |
| `name` | varchar(200) | NOT NULL |
| `description` | text | NOT NULL |
| `source` | varchar(20) | NOT NULL, index |
| `status` | varchar(10) | NOT NULL, index |
| `purchase_price` | decimal | NOT NULL |
| `selling_price` | decimal | NOT NULL |
| `min_stock` | integer unsigned | NOT NULL, CHECK >= 0 |
| `image` | varchar(100) | NULL |
| `category_id` | bigint | NOT NULL, FK → `catalog_category.id`, index |
| `brand_id` | bigint | NULL, FK → `catalog_brand.id`, index |
| `supplier_id` | bigint | NULL, FK → `suppliers_supplier.id`, index |

### 6.4 PRODUCT_VARIANT

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `sku` | varchar(64) | NOT NULL, UK, index |
| `barcode` | varchar(64) | NOT NULL, UK, index |
| `size` | varchar(16) | NOT NULL |
| `color` | varchar(64) | NOT NULL |
| `stock_quantity` | integer unsigned | NOT NULL, CHECK >= 0 |
| `selling_price` | decimal | NULL |
| `purchase_price` | decimal | NULL |
| `is_active` | bool | NOT NULL |
| `product_id` | bigint | NOT NULL, FK → `catalog_product.id`, index |
| UK bersama | `product_id` + `size` + `color` | — |

### 6.5 BARCODE

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `barcode_value` | varchar(64) | NOT NULL, UK, index |
| `format` | varchar(10) | NOT NULL |
| `is_active` | bool | NOT NULL |
| `product_variant_id` | bigint | NOT NULL, FK → `catalog_productvariant.id`, index |
| `regenerated_from_id` | bigint | NULL, FK → `catalog_barcode.id` (self), index |

### 6.6 Relasi Catalog

| Dari | Ke | Kardinalitas | Keterangan |
|---|---|---|---|
| CATEGORY | PRODUCT | 1 : N | Satu kategori bisa mengelompokkan banyak produk. |
| BRAND | PRODUCT | 1 : N | Satu brand bisa dipakai banyak produk (opsional). |
| SUPPLIER | PRODUCT | 1 : N | Satu pemasok bisa mengasokkan banyak produk (opsional). |
| PRODUCT | PRODUCT_VARIANT | 1 : N | Satu produk bisa punya banyak varian ukuran/warna. |
| PRODUCT_VARIANT | BARCODE | 1 : N | Satu varian bisa punya banyak barcode aktif/riwayat. |
| PRODUCT_VARIANT | TRANSACTION_ITEM | 1 : N | Satu varian bisa terjual di banyak item transaksi. |

---

## 7. Domain Pemasok (Suppliers)

### 7.1 SUPPLIER

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `supplier_id` | varchar(32) | NOT NULL, UK, index |
| `name` | varchar(150) | NOT NULL |
| `contact_person` | varchar(100) | NOT NULL |
| `phone` | varchar(32) | NOT NULL |
| `email` | varchar(254) | NOT NULL |
| `address` | text | NOT NULL |
| `supplier_type` | varchar(16) | NOT NULL, index |
| `notes` | text | NOT NULL |
| `created_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `updated_by_id` | bigint | NULL, FK → `accounts_user.id`, index |

### 7.2 Relasi Suppliers

| Dari | Ke | Kardinalitas | Keterangan |
|---|---|---|---|
| SUPPLIER | PRODUCT | 1 : N | Satu pemasok bisa mengasokkan banyak produk (opsional). |
| SUPPLIER | MATERIAL | 1 : N | Satu pemasok bisa mengasokkan banyak bahan baku (opsional). |

---

## 8. Domain Penjualan (Sales)

### 8.1 TRANSACTION

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `transaction_number` | varchar(64) | NOT NULL, UK, index |
| `transaction_date` | datetime | NOT NULL, index |
| `subtotal` | decimal | NOT NULL |
| `discount_amount` | decimal | NOT NULL |
| `grand_total` | decimal | NOT NULL |
| `payment_status` | varchar(20) | NOT NULL, index |
| `status` | varchar(20) | NOT NULL, index |
| `stock_deducted` | bool | NOT NULL |
| `notes` | text | NOT NULL |
| `customer_id` | bigint | NULL, FK → `customers_customer.id`, index |
| `cashier_id` | bigint | NOT NULL, FK → `accounts_user.id`, index |
| `created_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `updated_by_id` | bigint | NULL, FK → `accounts_user.id`, index |

### 8.2 TRANSACTION_ITEM

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `quantity` | integer unsigned | NOT NULL, CHECK >= 0 |
| `unit_price` | decimal | NOT NULL |
| `discount` | decimal | NOT NULL |
| `total` | decimal | NOT NULL |
| `transaction_id` | bigint | NOT NULL, FK → `sales_transaction.id`, index |
| `product_variant_id` | bigint | NOT NULL, FK → `catalog_productvariant.id`, index |

### 8.3 Relasi Sales

| Dari | Ke | Kardinalitas | Keterangan |
|---|---|---|---|
| TRANSACTION | TRANSACTION_ITEM | 1 : N | Satu transaksi terdiri dari banyak item. |
| TRANSACTION_ITEM | PRODUCT_VARIANT | N : 1 | Banyak item merujuk satu varian produk. |
| TRANSACTION | CUSTOMER | N : 1 | Banyak transaksi dimiliki satu customer (opsional). |
| TRANSACTION | USER (cashier) | N : 1 | Banyak transaksi dilayani satu kasir. |

---

## 9. Domain Pembayaran (Payments)

### 9.1 PAYMENT

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `amount` | decimal | NOT NULL |
| `method` | varchar(20) | NOT NULL |
| `status` | varchar(20) | NOT NULL, index |
| `payment_type` | varchar(16) | NOT NULL, index |
| `due_date` | date | NULL, index |
| `confirmed_at` | datetime | NULL |
| `payment_proof` | varchar(100) | NULL |
| `notes` | text | NOT NULL |
| `transaction_id` | bigint | NOT NULL, FK → `sales_transaction.id`, index |
| `confirmed_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `created_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `updated_by_id` | bigint | NULL, FK → `accounts_user.id`, index |

### 9.2 ORDER_PAYMENT

Pembayaran untuk **custom order** (DP / cicilan / pelunasan), terpisah dari `PAYMENT` yang menempel pada transaksi POS.

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `amount` | decimal | NOT NULL |
| `payment_type` | varchar(16) | NOT NULL, index (FULL/DP/INSTALLMENT) |
| `method` | varchar(20) | NOT NULL (CASH/BANK_TRANSFER/QRIS) |
| `status` | varchar(20) | NOT NULL, index (PENDING/CONFIRMED/REFUNDED/FAILED) |
| `payment_proof` | varchar(100) | NULL |
| `due_date` | date | NULL, index (jatuh tempo DP/cicilan) |
| `confirmed_at` | datetime | NULL |
| `notes` | text | NOT NULL |
| `confirmed_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `created_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `order_id` | bigint | NOT NULL, FK → `orders_order.id`, index |
| `updated_by_id` | bigint | NULL, FK → `accounts_user.id`, index |

Index kustom: `(order_id, created_at DESC)`, `status`, `payment_type`, `due_date`.

### 9.3 Relasi Payments

| Dari | Ke | Kardinalitas | Keterangan |
|---|---|---|---|
| TRANSACTION | PAYMENT | 1 : N | Satu transaksi POS bisa punya banyak pembayaran (DP/cicilan/pelunasan). |
| PAYMENT | USER (confirmed_by) | N : 1 | Banyak pembayaran dikonfirmasi satu petugas (opsional). |
| ORDER | ORDER_PAYMENT | 1 : N | Satu custom order bisa punya banyak pembayaran (DP/cicilan/pelunasan). |
| ORDER_PAYMENT | USER (confirmed_by) | N : 1 | Banyak pembayaran order dikonfirmasi satu petugas (opsional). |

Catatan: `ORDER.dp_amount` disinkronkan dengan total `ORDER_PAYMENT` berstatus CONFIRMED (dihitung ulang saat confirm/void); `remaining_balance = total_amount - dp_amount`.

---

## 10. Domain Inventori (Inventory)

### 10.1 MATERIAL

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `material_id` | varchar(32) | NOT NULL, UK, index |
| `name` | varchar(150) | NOT NULL |
| `category` | varchar(20) | NOT NULL, index |
| `unit` | varchar(10) | NOT NULL |
| `stock_quantity` | decimal | NOT NULL |
| `min_stock` | decimal | NOT NULL |
| `purchase_price` | decimal | NOT NULL |
| `notes` | text | NOT NULL |
| `supplier_id` | bigint | NULL, FK → `suppliers_supplier.id`, index |
| `created_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `updated_by_id` | bigint | NULL, FK → `accounts_user.id`, index |

### 10.2 STOCK_MOVEMENT

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `object_id` | integer unsigned | NOT NULL, CHECK >= 0 |
| `movement_type` | varchar(24) | NOT NULL, index |
| `quantity` | decimal | NOT NULL |
| `previous_stock` | decimal | NOT NULL |
| `new_stock` | decimal | NOT NULL |
| `reference` | varchar(100) | NOT NULL |
| `notes` | text | NOT NULL |
| `content_type_id` | integer | NOT NULL, FK → `django_content_type.id`, index |
| `user_id` | bigint | NULL, FK → `accounts_user.id`, index |

### 10.3 Relasi Inventory

| Dari | Ke | Kardinalitas | Keterangan |
|---|---|---|---|
| MATERIAL | MATERIAL_REQUEST | 1 : N | Satu material bisa muncul di banyak permintaan bahan. |
| MATERIAL | MATERIAL_USAGE | 1 : N | Satu material bisa dipakai di banyak produksi. |
| SUPPLIER | MATERIAL | 1 : N | Satu pemasok bisa mengasokkan banyak bahan (opsional). |
| DJANGO_CONTENT_TYPE | STOCK_MOVEMENT | 1 : N | Satu content type dipakai banyak stock movement (polimorfik). |
| USER | STOCK_MOVEMENT | 1 : N | Satu user bisa mencatat banyak gerakan stok. |

---

## 11. Domain Produksi (Production)

### 11.1 PRODUCTION

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `production_id` | varchar(32) | NOT NULL, UK, index |
| `start_date` | date | NULL |
| `estimated_completion` | date | NULL |
| `actual_completion` | date | NULL |
| `progress` | integer unsigned | NOT NULL, CHECK >= 0 |
| `status` | varchar(20) | NOT NULL, index |
| `notes` | text | NOT NULL |
| `order_id` | bigint | NOT NULL, FK → `orders_order.id`, index |
| `designer_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `created_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `updated_by_id` | bigint | NULL, FK → `accounts_user.id`, index |

### 11.2 MATERIAL_REQUEST

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `request_id` | varchar(32) | NOT NULL, UK, index |
| `status` | varchar(16) | NOT NULL, index |
| `quantity` | decimal | NOT NULL |
| `notes` | text | NOT NULL |
| `production_id` | bigint | NOT NULL, FK → `production_production.id`, index |
| `material_id` | bigint | NOT NULL, FK → `inventory_material.id`, index |
| `requested_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `approved_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `created_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `updated_by_id` | bigint | NULL, FK → `accounts_user.id`, index |

### 11.3 MATERIAL_USAGE

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `usage_id` | varchar(32) | NOT NULL, UK, index |
| `quantity_used` | decimal | NOT NULL |
| `used_at` | datetime | NOT NULL, index |
| `notes` | text | NOT NULL |
| `production_id` | bigint | NOT NULL, FK → `production_production.id`, index |
| `material_request_id` | bigint | NULL, FK → `production_materialrequest.id`, index |
| `material_id` | bigint | NOT NULL, FK → `inventory_material.id`, index |
| `used_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `created_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `updated_by_id` | bigint | NULL, FK → `accounts_user.id`, index |

### 11.4 FITTING

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `fitting_id` | varchar(32) | NOT NULL, UK, index |
| `scheduled_date` | datetime | NOT NULL, index |
| `fitting_date` | datetime | NULL |
| `results` | text | NOT NULL |
| `alterations_required` | text | NOT NULL |
| `documentation` | varchar(100) | NULL |
| `status` | varchar(16) | NOT NULL, index |
| `order_id` | bigint | NOT NULL, FK → `orders_order.id`, index |
| `customer_id` | bigint | NOT NULL, FK → `customers_customer.id`, index |
| `created_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `updated_by_id` | bigint | NULL, FK → `accounts_user.id`, index |

### 11.5 QUALITY_CONTROL

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `qc_id` | varchar(32) | NOT NULL, UK, index |
| `stitching_quality` | bool | NOT NULL |
| `size_accuracy` | bool | NOT NULL |
| `fabric_quality` | bool | NOT NULL |
| `color_consistency` | bool | NOT NULL |
| `design_conformity` | bool | NOT NULL |
| `cleanliness` | bool | NOT NULL |
| `final_appearance` | bool | NOT NULL |
| `status` | varchar(20) | NOT NULL, index |
| `qc_date` | datetime | NULL |
| `notes` | text | NOT NULL |
| `order_id` | bigint | NOT NULL, FK → `orders_order.id`, index |
| `qc_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `created_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `updated_by_id` | bigint | NULL, FK → `accounts_user.id`, index |

### 11.6 Relasi Production

| Dari | Ke | Kardinalitas | Keterangan |
|---|---|---|---|
| ORDER | PRODUCTION | 1 : N | Satu order bisa punya banyak rekam produksi. |
| ORDER | FITTING | 1 : N | Satu order bisa punya banyak sesi fitting. |
| ORDER | QUALITY_CONTROL | 1 : N | Satu order bisa punya banyak catatan QC. |
| PRODUCTION | MATERIAL_REQUEST | 1 : N | Satu produksi bisa punya banyak permintaan bahan. |
| PRODUCTION | MATERIAL_USAGE | 1 : N | Satu produksi bisa punya banyak pemakaian bahan. |
| MATERIAL_REQUEST | MATERIAL_USAGE | 1 : N | Satu permintaan bahan bisa direalisasikan banyak pemakaian. |
| USER | PRODUCTION | 1 : N | Satu desainer bisa menangani banyak produksi. |
| USER | MATERIAL_REQUEST | 1 : N | Satu user bisa mengajukan/menyetujui banyak request. |
| USER | MATERIAL_USAGE | 1 : N | Satu user bisa mencatat banyak pemakaian. |
| USER | QUALITY_CONTROL | 1 : N | Satu user bisa QC banyak order. |

---

## 12. Domain Desain (Designs)

### 12.1 DESIGN

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `design_id` | varchar(32) | NOT NULL, UK, index |
| `name` | varchar(150) | NOT NULL |
| `category` | varchar(20) | NOT NULL |
| `sketch` | varchar(100) | NULL |
| `customer_reference` | varchar(100) | NULL |
| `fabric` | varchar(100) | NOT NULL |
| `color` | varchar(100) | NOT NULL |
| `style_description` | text | NOT NULL |
| `version` | integer unsigned | NOT NULL, CHECK >= 0 |
| `status` | varchar(20) | NOT NULL, index |
| `estimated_cost` | decimal | NOT NULL |
| `estimated_duration_days` | integer unsigned | NOT NULL, CHECK >= 0 |
| `notes` | text | NOT NULL |
| `order_id` | bigint | NOT NULL, FK → `orders_order.id`, index |
| `designer_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `created_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| `updated_by_id` | bigint | NULL, FK → `accounts_user.id`, index |

### 12.2 DESIGN_VERSION

| Kolom | Tipe | Constraint |
|---|---|---|
| `id` | integer | PK, autoincrement |
| `created_at` | datetime | NOT NULL, index |
| `updated_at` | datetime | NOT NULL |
| `version_number` | integer unsigned | NOT NULL, CHECK >= 0 |
| `sketch` | varchar(100) | NULL |
| `notes` | text | NOT NULL |
| `design_id` | bigint | NOT NULL, FK → `designs_design.id`, index |
| `created_by_id` | bigint | NULL, FK → `accounts_user.id`, index |
| UK bersama | `design_id` + `version_number` | — |

### 12.3 Relasi Designs

| Dari | Ke | Kardinalitas | Keterangan |
|---|---|---|---|
| ORDER | DESIGN | 1 : N | Satu order bisa punya banyak desain. |
| DESIGN | DESIGN_VERSION | 1 : N | Satu desain bisa punya banyak revisi/versi. |
| USER | DESIGN | 1 : N | Satu desainer bisa membuat banyak desain. |
| USER | DESIGN_VERSION | 1 : N | Satu user bisa membuat banyak versi desain. |

---

## 13. Relasi Polimorfik (ContentType)

### 13.1 Cara Kerja

`django_content_type` menyimpan pasangan `(app_label, model)` untuk setiap model Django. `inventory_stockmovement` memakai dua kolom untuk merujuk objek apa pun:
- `content_type_id` → `django_content_type.id`
- `object_id` → `id` objek target (integer)

Relasi ini tidak bisa didefinisikan sebagai FK biasa di level database, karena targetnya bisa `catalog_productvariant` atau `inventory_material`. Integritas dijaga di level aplikasi (Django generic foreign key).

### 13.2 Tabel yang Terlibat

| Tabel | Kolom | Keterangan |
|---|---|---|
| `django_content_type` | `id` PK, `app_label`, `model`, UK `(app_label, model)` | Menyimpan tipe konten |
| `inventory_stockmovement` | `content_type_id` FK, `object_id` integer | Polimorfik ke `catalog_productvariant` atau `inventory_material` |

### 13.3 Contoh Data

| app_label | model | arti |
|---|---|---|
| `catalog` | `productvariant` | stok barang jadi (produk) |
| `inventory` | `material` | stok bahan baku |

### 13.4 Alur

Setiap kali stok berubah, aplikasi membuat `STOCK_MOVEMENT` dengan:
- `content_type_id` = id `ProductVariant` atau `Material`
- `object_id` = primary key varian/material tersebut
- `movement_type` = `PURCHASE_IN`, `SALE_OUT`, `PRODUCTION_USAGE`, `RETURN`, `ADJUSTMENT`, `DAMAGE_LOSS`
- `previous_stock`, `new_stock`, `quantity`, `reference`, `notes`, `user_id`

---

## 14. Relasi Self-Reference (Barcode)

### 14.1 Cara Kerja

`catalog_barcode` memiliki FK ke dirinya sendiri: `regenerated_from_id` → `catalog_barcode.id`. Ini mencatat barcode mana yang diregenerasi dari barcode lain.

### 14.2 Contoh

| id | barcode_value | regenerated_from_id | arti |
|---|---|---|---|
| 1 | `VEL-0001` | NULL | barcode asli |
| 2 | `VEL-0002` | 1 | barcode baru hasil regenerasi dari VEL-0001 |

---

## 15. Relasi Audit (created_by / updated_by)

### 15.1 Kolom Audit

Hampir semua tabel bisnis (dari `BaseModel` + `AuditMixin`) memiliki:
- `created_at` datetime — waktu record dibuat
- `updated_at` datetime — waktu record terakhir diubah
- `created_by_id` bigint FK → `accounts_user.id` — user yang membuat (nullable)
- `updated_by_id` bigint FK → `accounts_user.id` — user yang mengubah terakhir (nullable)

### 15.2 Tabel yang Memakai AuditMixin

| Tabel | created_by | updated_by |
|---|---|---|
| `CUSTOMER` | ya | ya |
| `MEASUREMENT` | ya | ya |
| `ORDER` | ya | ya |
| `ORDER_STATUS_HISTORY` | tidak | tidak |
| `PRODUCTION` | ya | ya |
| `MATERIAL_REQUEST` | ya | ya |
| `MATERIAL_USAGE` | ya | ya |
| `FITTING` | ya | ya |
| `QUALITY_CONTROL` | ya | ya |
| `DESIGN` | ya | ya |
| `DESIGN_VERSION` | `created_by_id` saja | tidak ada `updated_by_id` (hanya `created_at`) |
| `SUPPLIER` | ya | ya |
| `MATERIAL` | ya | ya |
| `PAYMENT` | ya | ya |
| `TRANSACTION` | ya | ya |
| `BARCODE` | tidak | tidak |
| `TRANSACTION_ITEM` | tidak | tidak |
| `PRODUCT` (catalog) | tidak | tidak (Product tidak pakai AuditMixin) |
| `PRODUCT_VARIANT` | tidak | tidak |
| `STOCK_MOVEMENT` | `user_id` (bukan created_by/updated_by) | — |

### 15.3 Catatan

- `created_by_id` dan `updated_by_id` nullable, karena user bisa dihapus (`SET_NULL`) tanpa menghapus record bisnis.
- `STOCK_MOVEMENT` tidak memakai `AuditMixin`, tapi memakai `user_id` untuk mencatat siapa yang mencatat gerakan stok.

---

## 16. Unique Constraint dan Index Penting

### 16.1 Unique Key

| Tabel | Kolom UK | Keterangan |
|---|---|---|
| `accounts_role` | `code` | kode role unik |
| `accounts_user` | `username` | username login unik |
| `customers_customer` | `customer_id` | ID pelanggan unik |
| `customers_measurement` | `measurement_id` | ID measurement unik |
| `orders_order` | `order_number` | nomor order unik |
| `catalog_category` | `name`, `slug` | nama dan slug kategori unik |
| `catalog_brand` | `name`, `slug` | nama dan slug brand unik |
| `catalog_product` | `sku` | SKU produk unik |
| `catalog_productvariant` | `sku`, `barcode`, `(product_id, size, color)` | SKU, barcode, dan kombinasi varian unik |
| `catalog_barcode` | `barcode_value` | nilai barcode unik |
| `suppliers_supplier` | `supplier_id` | ID pemasok unik |
| `sales_transaction` | `transaction_number` | nomor transaksi unik |
| `payments_payment` | — | tidak ada UK tunggal |
| `payments_orderpayment` | — | tidak ada UK tunggal |
| `inventory_material` | `material_id` | ID material unik |
| `production_production` | `production_id` | ID produksi unik |
| `production_materialrequest` | `request_id` | ID request unik |
| `production_materialusage` | `usage_id` | ID usage unik |
| `production_fitting` | `fitting_id` | ID fitting unik |
| `production_qualitycontrol` | `qc_id` | ID QC unik |
| `designs_design` | `design_id` | ID desain unik |
| `designs_designversion` | `(design_id, version_number)` | versi desain unik per desain |

### 16.2 Index Penting (non-unique)

| Tabel | Index | Tujuan |
|---|---|---|
| `customers_customer` | `customer_id`, `email`, `phone` | pencarian cepat customer |
| `customers_measurement` | `(customer_id, measurement_date DESC)` | riwayat ukuran per customer |
| `customers_measurement` | `order_id` | measurement per order |
| `orders_order` | `(status, order_date DESC)` | order aktif per status |
| `orders_order` | `(designer_id, order_date DESC)` | order per desainer |
| `orders_order` | `cashier_id`, `customer_id`, `order_date` | filter order |
| `orders_orderstatushistory` | `(order_id, changed_at DESC)` | riwayat status per order |
| `catalog_product` | `sku`, `source`, `status` | filter produk |
| `catalog_productvariant` | `sku`, `barcode`, `product_id` | lookup varian |
| `catalog_barcode` | `barcode_value`, `product_variant_id` | lookup barcode |
| `sales_transaction` | `(cashier_id, transaction_date DESC)` | transaksi per kasir |
| `sales_transaction` | `(status, payment_status)` | filter status transaksi |
| `payments_payment` | `(transaction_id, created_at DESC)` | pembayaran per transaksi |
| `payments_orderpayment` | `(order_id, created_at DESC)`, `status`, `payment_type`, `due_date` | pembayaran custom order per order & filter |
| `inventory_material` | `material_id`, `category` | lookup material |
| `inventory_stockmovement` | `(content_type_id, object_id)` | ledger per objek |
| `inventory_stockmovement` | `(movement_type, created_at DESC)` | ledger per jenis gerakan |
| `production_production` | `(status, created_at DESC)` | produksi aktif |
| `production_materialrequest` | `(status, created_at DESC)` | request pending/fulfilled |
| `production_fitting` | `(status, scheduled_date DESC)` | jadwal fitting |
| `production_qualitycontrol` | `(status, created_at DESC)` | QC pending |
| `designs_design` | `(status, created_at DESC)` | desain pending approval |
| `designs_design` | `(designer_id, created_at DESC)` | desain per desainer |

---

## 17. Ringkasan Kardinalitas

| Kelompok | Jumlah Relasi |
|---|---|
| Akses dan pengguna (ROLE-USER + USER-*) | 13 |
| Pelanggan (CUSTOMER-MEASUREMENT, CUSTOMER-ORDER, CUSTOMER-FITTING, CUSTOMER-TRANSACTION, MEASUREMENT-ORDER) | 5 |
| Pesanan (ORDER-*) | 6 |
| Katalog (CATEGORY-PRODUCT, BRAND-PRODUCT, SUPPLIER-PRODUCT, PRODUCT-PRODUCT_VARIANT, PRODUCT_VARIANT-BARCODE, PRODUCT_VARIANT-TRANSACTION_ITEM, BARCODE-BARCODE self) | 7 |
| Pemasok (SUPPLIER-MATERIAL) | 1 |
| Penjualan (TRANSACTION-TRANSACTION_ITEM, TRANSACTION_ITEM-PRODUCT_VARIANT) | 2 |
| Pembayaran (TRANSACTION-PAYMENT, PAYMENT-USER, ORDER-ORDER_PAYMENT, ORDER_PAYMENT-USER) | 4 |
| Inventori (MATERIAL-MATERIAL_REQUEST, MATERIAL-MATERIAL_USAGE, USER-STOCK_MOVEMENT, DJANGO_CONTENT_TYPE-STOCK_MOVEMENT) | 4 |
| Produksi (ORDER-PRODUCTION, ORDER-FITTING, ORDER-QUALITY_CONTROL, PRODUCTION-MATERIAL_REQUEST, PRODUCTION-MATERIAL_USAGE, MATERIAL_REQUEST-MATERIAL_USAGE, USER-PRODUCTION, USER-MATERIAL_REQUEST, USER-MATERIAL_USAGE, USER-QUALITY_CONTROL) | 10 |
| Desain (ORDER-DESIGN, DESIGN-DESIGN_VERSION, USER-DESIGN, USER-DESIGN_VERSION) | 4 |
| Sistem (USER-DJANGO_ADMIN_LOG, DJANGO_CONTENT_TYPE-AUTH_PERMISSION, DJANGO_CONTENT_TYPE-DJANGO_ADMIN_LOG) | 3 |
| **Total** | **59 relasi** |

---

## 18. Alur Bisnis dan Relasinya

### 18.1 Alur Custom Order (Couture)

```
CUSTOMER (member)
    │
    ▼
ORDER (dibuat cashier/designer)
    │
    ├──► MEASUREMENT (data ukuran, opsional diikat ke order)
    ├──► DESIGN (1:N, dibuat designer)
    │       │
    │       ▼
    │   DESIGN_VERSION (1:N, setiap revisi/approval jadi snapshot)
    │
    ├──► PRODUCTION (1:N, rekam produksi)
    │       │
    │       ├──► MATERIAL_REQUEST (1:N, minta bahan)
    │       │       │
    │       │       ▼
    │       │   MATERIAL_USAGE (1:N, realisasi pemakaian; potong stok MATERIAL)
    │       │
    │       └──► MATERIAL_USAGE langsung (tanpa request)
    │
    ├──► FITTING (1:N, sesi fitting dengan customer)
    │
    ├──► ORDER_PAYMENT (1:N, DP/cicilan/lunas; sinkronkan dp_amount order)
    │
    └──► QUALITY_CONTROL (1:N, pemeriksaan sebelum diserahkan)
```

### 18.2 Alur Penjualan POS

```
CUSTOMER (opsional)
    │
    ▼
TRANSACTION (dibuat cashier, status PENDING, stok belum dipotong)
    │
    ├──► TRANSACTION_ITEM (1:N, item yang dibeli)
    │       │
    │       ▼
    │   PRODUCT_VARIANT (N:1, barang yang dijual)
    │
    └──► PAYMENT (1:N, DP/cicilan/pelunasan)
            │
            ▼
        CONFIRMED → TRANSACTION.payment_status = PAID/COMPLETED
            │
            ▼
        STOCK_MOVEMENT (type=SALE_OUT, kurangi stok PRODUCT_VARIANT)
```

### 18.3 Alur Refund

```
PAYMENT (CONFIRMED, dibatalkan)
    │
    ▼
STOCK_MOVEMENT (type=RETURN, kembalikan stok PRODUCT_VARIANT)
    │
    ▼
TRANSACTION.status = REFUNDED (jika pembayaran tidak menutupi grand total)
```

### 18.4 Alur Material

```
MATERIAL (stok bahan baku)
    │
    ▼
MATERIAL_REQUEST (designer/production minta bahan)
    │
    ▼
MATERIAL_USAGE (pemakaian aktual, potong stok MATERIAL via STOCK_MOVEMENT type=PRODUCTION_USAGE)
```

### 18.5 Alur Audit

Setiap perubahan data bisnis dicatat:
- `created_at` / `updated_at` otomatis oleh `BaseModel`
- `created_by_id` / `updated_by_id` dari user yang login (`AuditMixin`)
- `STOCK_MOVEMENT` mencatat setiap perubahan stok dengan `user_id`
- `ORDER_STATUS_HISTORY` mencatat setiap perubahan status order dengan `changed_by_id`

---

## Lampiran A — Daftar Tabel

| No | Tabel | Domain |
|---|---|---|
| 1 | `accounts_role` | Accounts |
| 2 | `accounts_user` | Accounts |
| 3 | `customers_customer` | Customers |
| 4 | `customers_measurement` | Customers |
| 5 | `orders_order` | Orders |
| 6 | `orders_orderstatushistory` | Orders |
| 7 | `catalog_category` | Catalog |
| 8 | `catalog_brand` | Catalog |
| 9 | `catalog_product` | Catalog |
| 10 | `catalog_productvariant` | Catalog |
| 11 | `catalog_barcode` | Catalog |
| 12 | `suppliers_supplier` | Suppliers |
| 13 | `sales_transaction` | Sales |
| 14 | `sales_transactionitem` | Sales |
| 15 | `payments_payment` | Payments |
| 16 | `payments_orderpayment` | Payments |
| 17 | `inventory_material` | Inventory |
| 18 | `inventory_stockmovement` | Inventory |
| 19 | `production_production` | Production |
| 20 | `production_materialrequest` | Production |
| 21 | `production_materialusage` | Production |
| 22 | `production_fitting` | Production |
| 23 | `production_qualitycontrol` | Production |
| 24 | `designs_design` | Designs |
| 25 | `designs_designversion` | Designs |
| 26 | `django_content_type` | System |
| 27 | `django_migrations` | System |
| 28 | `django_session` | System |
| 29 | `django_admin_log` | System |
| 30 | `auth_group` | System |
| 31 | `auth_permission` | System |
| 32 | `auth_group_permissions` | System |
| 33 | `accounts_user_groups` | System |
| 34 | `accounts_user_user_permissions` | System |
| 35 | `sqlite_sequence` | System (internal SQLite) |

---

## Lampiran B — Keterangan Tipe Data SQLite

| Tipe SQLite | Arti | Contoh |
|---|---|---|
| `integer` | bilangan bulat, autoincrement untuk PK | `id` |
| `integer unsigned` | bilangan bulat tanpa tanda, dengan CHECK >= 0 | `stock_quantity`, `progress` |
| `varchar(n)` | teks dengan panjang maksimal n | `username`, `sku` |
| `text` | teks panjang | `notes`, `description` |
| `decimal` | bilangan desimal (disimpan sebagai TEXT di SQLite, tapi dianggap NUMERIC oleh Django) | `total_amount`, `grand_total` |
| `date` | tanggal (YYYY-MM-DD) | `required_date` |
| `datetime` | tanggal dan waktu (YYYY-MM-DD HH:MM:SS) | `created_at`, `order_date` |
| `bool` | boolean (0/1) | `is_active`, `stock_deducted` |
| `bigint` | bilangan bulat besar, dipakai untuk FK ke `integer id` | `role_id`, `customer_id` |
