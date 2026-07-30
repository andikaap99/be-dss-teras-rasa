# Rangkuman Produk: DSS Penjualan UMKM Teras Rasa

## 1. Gambaran Umum

**Nama Produk:** Decision Support System (DSS) Penjualan UMKM Teras Rasa

**Jenis:** Sistem Pendukung Keputusan berbasis web untuk prediksi dan analisis penjualan UMKM (Usaha Mikro, Kecil, dan Menengah) di bidang kuliner.

**Domain Bisnis:** UMKM penjual mie ayam dan berbagai jenis jus (alpukat, mangga, jeruk, jambu, strobery). Sistem ini membantu pemilik usaha mengambil keputusan berbasis data terkait stok, perencanaan produksi, dan proyeksi omzet harian.

**Stack Teknologi Utama:**
- **Backend:** Python 3.12, FastAPI (async web framework)
- **Database:** MySQL (`dss_mie_ayam`), SQLAlchemy ORM, PyMySQL driver
- **Machine Learning:** TensorFlow 2.20 (LSTM), scikit-learn 1.8 (MinMaxScaler), joblib
- **Infrastruktur:** APScheduler (background job), uvicorn (ASGI server)
- **Auth:** JWT (PyJWT), bcrypt (password hashing)

---

## 2. Arsitektur Sistem

```
┌──────────────────────────────────────────────────────────┐
│                    Client (Frontend)                     │
│              (belum ada di codebase ini)                 │
└───────────────────────────┬──────────────────────────────┘
                            │ HTTP REST API
┌───────────────────────────▼──────────────────────────────┐
│                     FastAPI Server                        │
│                    (main.py)                              │
│                                                          │
│  ┌────────────────┐  ┌──────────────────────────────┐   │
│  │   APScheduler   │  │    BackgroundScheduler       │   │
│  │  Cron 17:00/Hari│  │  → retrain_lstm_model()     │   │
│  └────────┬───────┘  └──────────────┬───────────────┘   │
│           │                         │                    │
│  ┌────────▼─────────────────────────▼──────────────┐    │
│  │              API Router (/api)                   │    │
│  │                                                  │    │
│  │  auth.py      → POST /api/login                 │    │
│  │  upload.py    → POST /api/upload-harian          │    │
│  │  analytics.py → GET  /api/kpi                   │    │
│  │                 GET  /api/omzet-trend             │    │
│  │                 GET  /api/menu-composition        │    │
│  │  predict.py   → GET  /api/predict-omzet          │    │
│  │  train.py     → GET  /api/train-status           │    │
│  │                 POST /api/retrain-manual          │    │
│  └────────┬────────────────────────┬───────────────┘    │
│           │                        │                     │
└───────────┼────────────────────────┼─────────────────────┘
            │                        │
   ┌────────▼────────┐    ┌──────────▼──────────────────┐
   │  MySQL Database  │    │    Model Artifacts (disk)   │
   │  (dss_mie_ayam)  │    │                              │
   │                   │    │  model/                      │
   │  - users table    │    │  ├── *_lstm_model.h5 (6x)   │
   │  - sales table    │    │  ├── *_scaler.pkl (6x)      │
   │                   │    │  ├── metadata.json           │
   └──────────────────┘    │  └── data_clean.csv          │
                           └──────────────────────────────┘
```

---

## 3. Struktur Direktori

```
backend/
├── main.py                    # Entry point, setup FastAPI + APScheduler
├── create_user.py             # Script satu kali buat user admin
├── requirements.txt           # Dependencies Python
├── .env                       # Secret key JWT
├── .gitignore
├── alembic.ini                # (kosong, belum dikonfigurasi)
├── readme.md                  # Dokumentasi API (Bahasa Indonesia)
│
├── app/
│   ├── __init__.py
│   ├── database/
│   │   └── database.py        # SQLAlchemy engine, session, Base
│   ├── models/
│   │   ├── user.py            # ORM model: users table
│   │   └── sales.py           # ORM model: sales table
│   ├── schemas/
│   │   └── user.py            # Pydantic: UserLogin (request body)
│   ├── api/
│   │   ├── auth.py            # POST /api/login
│   │   ├── upload.py          # POST /api/upload-harian
│   │   ├── analytics.py       # GET /api/kpi, /omzet-trend, /menu-composition
│   │   ├── predict.py         # GET /api/predict-omzet
│   │   └── train.py           # GET /api/train-status, POST /api/retrain-manual
│   ├── services/
│   │   └── trainer.py         # Fungsi retrain_lstm_model (stub) + get_last_trained_time
│   ├── ml_models/             # Copy model .h5 (runtime inference)
│   ├── core/                  # (kosong)
│   └── utils/                 # (kosong)
│
├── model/
│   ├── lstm_training.ipynb    # Notebook training LSTM
│   ├── DataPenjualanUMKMTerasRasa.xlsx  # Data mentah
│   ├── data_clean.csv         # Data bersih (181 hari, Jan-Jun 2026)
│   ├── metadata.json          # Hyperparameter + metrik tiap model
│   ├── *_lstm_model.h5 (6x)   # Bobot model LSTM per menu
│   └── *_scaler.pkl (6x)      # MinMaxScaler per menu (via joblib)
│
└── .venv/                     # Virtual environment Python 3.12
```

---

## 4. Skema Database

### Tabel `users`
| Kolom         | Tipe         | Constraint            | Keterangan                     |
|---------------|--------------|-----------------------|--------------------------------|
| id            | Integer      | PRIMARY KEY, AUTO INC | ID unik user                   |
| username      | String(50)   | UNIQUE, NOT NULL      | Username login                 |
| password_hash | String(255)  | NOT NULL              | Password bcrypt (hashed)       |

### Tabel `sales`
| Kolom     | Tipe    | Constraint              | Default | Keterangan                        |
|-----------|---------|-------------------------|---------|-----------------------------------|
| id        | Integer | PRIMARY KEY, AUTO INC   | -       | ID unik record                    |
| date      | Date    | UNIQUE, NOT NULL        | -       | Satu record per hari (upsert)     |
| mie_ayam  | Integer | -                       | 0       | Porsi mie ayam terjual            |
| alpukat   | Integer | -                       | 0       | Porsi jus alpukat terjual         |
| mangga    | Integer | -                       | 0       | Porsi jus mangga terjual          |
| jeruk     | Integer | -                       | 0       | Porsi jus jeruk terjual           |
| jambu     | Integer | -                       | 0       | Porsi jus jambu terjual           |
| strobery  | Integer | -                       | 0       | Porsi jus stroberi terjual        |
| omzet     | Integer | -                       | 0       | Total omzet harian (dihitung otomatis) |

**Catatan:** Kolom `date` memiliki `unique=True` sehingga upload data dengan tanggal yang sama akan melakukan update (replace), bukan insert duplikat.

---

## 5. API Endpoints

| Method | Endpoint               | Auth   | Fungsi                                                      |
|--------|------------------------|--------|-------------------------------------------------------------|
| GET    | `/`                    | Tidak  | Health check: "Website Online!"                             |
| POST   | `/api/login`           | Tidak  | Login → dapatkan JWT token (berlaku 24 jam)                 |
| POST   | `/api/upload-harian`   | Tidak  | Upload file Excel (.xlsx) → upsert data penjualan harian    |
| GET    | `/api/kpi`             | Tidak  | KPI 7 hari: total porsi mie ayam, jus terlaris & tersepi    |
| GET    | `/api/omzet-trend`     | Tidak  | Tren omzet 7 hari terakhir (untuk line chart)               |
| GET    | `/api/menu-composition`| Tidak  | Komposisi 5 menu terlaris 7 hari (untuk pie chart)          |
| GET    | `/api/predict-omzet`   | Tidak  | Prediksi omzet besok pakai LSTM (per menu + total)          |
| GET    | `/api/train-status`    | Tidak  | Status model + waktu terakhir training                      |
| POST   | `/api/retrain-manual`  | Tidak  | Trigger retrain manual di background                         |

**Catatan:** Meskipun JWT auth tersedia, endpoint selain login belum mewajibkan token. Semua endpoint kecuali login bisa diakses tanpa autentikasi.

---

## 6. Data Flow & Proses Bisnis

### 6.1 Upload Data Harian
1. User upload file Excel berisi rekap penjualan (kolom: `date`, `mie ayam`, `alpukat`, `mangga`, `jeruk`, `jambu`, `strobery`)
2. Sistem membaca Excel via pandas
3. Untuk setiap baris, omzet dihitung otomatis:
   - mie ayam = porsi × Rp15.000
   - alpukat = porsi × Rp12.000
   - mangga = porsi × Rp12.000
   - jeruk = porsi × Rp10.000
   - jambu = porsi × Rp10.000
   - strobery = porsi × Rp12.000
4. Jika tanggal sudah ada di DB → update record (replace). Jika belum → insert baru.
5. Jika tanggal yang di-upload = tanggal hari ini → flag `is_data_uploaded_today = True`

### 6.2 Dashboard Analytics
- **KPI:** Query 7 hari terakhir → total porsi mie ayam, jus terlaris, jus tersepi
- **Omzet Trend:** Query 7 hari terakhir → array labels (tanggal) + array data (omzet) untuk line chart
- **Menu Composition:** Aggregasi 7 hari → top 5 menu berdasarkan total porsi untuk pie chart

### 6.3 Prediksi Omzet (LSTM)
1. Validasi: data hari ini harus sudah di-upload + minimal 7 hari historis
2. Ambil 7 hari data terakhir dari DB
3. Untuk setiap menu (6 menu):
   - Ambil array porsi 7 hari → scale dengan MinMaxScaler → reshape ke (1, 7, 1)
   - Feed ke model LSTM → dapat prediksi porsi besok
   - Inverse scale → kalikan dengan harga satuan → dapat omzet per menu
4. Hitung total estimasi omzet
5. Return detail per menu + total

### 6.4 Retraining Model
- **Otomatis:** APScheduler menjalankan `retrain_lstm_model()` setiap jam 17:00
- **Manual:** POST `/api/retrain-manual` → jalankan di FastAPI BackgroundTasks
- **Status:** GET `/api/train-status` → status "Ready" + waktu terakhir file .h5 dimodifikasi
- **Catatan:** Fungsi retrain saat ini masih **stub** (placeholder), belum ada logika training aktual

---

## 7. Machine Learning Pipeline

### 7.1 Data
- **Sumber:** `DataPenjualanUMKMTerasRasa.xlsx` (data penjualan UMKM)
- **Preprocessing (di notebook):**
  - Isi nilai kosong strobery menggunakan rata-rata jus lainnya
  - Map tanggal asli (Nov 2021 - Apr 2022) ke target (Jan-Jun 2026) via interpolasi linear
  - Output: `data_clean.csv` (181 hari data)
- **Karakteristik:** Banyak baris bernilai 0 (hari tutup). Mie ayam konsisten menjadi item terlaris (0-51 porsi/hari).

### 7.2 Arsitektur Model
- **Tipe:** LSTM (Long Short-Term Memory) - 1 model per menu item
- **Arsitektur per model:**
  ```
  Input(SEQ_LENGTH, 1)
  → LSTM(units, return_sequences=True) + Dropout(0.2)
  → LSTM(units/2) + Dropout(0.2)
  → Dense(32, activation='relu')
  → Dense(1)
  ```
- **Loss:** MSE (Mean Squared Error)
- **Optimizer:** Adam
- **Metrik evaluasi:** MAE, RMSE, MAPE

### 7.3 Hyperparameter Tuning
Grid search dilakukan untuk setiap menu dengan kombinasi:
- `seq_length`: [7, 14, 30]
- `lstm_units`: [32, 64, 128]
- `learning_rate`: [0.001, 0.0005]

Total 18 kombinasi per menu. Dipilih yang memiliki MAE terendah.

### 7.4 Hasil Training (metadata.json)
| Menu     | Seq Length | LSTM Units | LR    | MAE    | RMSE   | MAPE (%) |
|----------|------------|------------|-------|--------|--------|----------|
| Mie Ayam | 7          | 64         | 0.001 | 9.1873 | 11.697 | 26.31    |
| Alpukat  | 7          | 64         | 0.001 | 2.2171 | 2.707  | 35.28    |
| Mangga   | 7          | 128        | 0.001 | 2.4395 | 3.116  | 28.51    |
| Jeruk    | 7          | 32         | 0.001 | 3.0212 | 3.559  | 44.27    |
| Jambu    | 7          | 32         | 0.001 | 1.1534 | 1.611  | 59.50    |
| Strobery | 7          | 128        | 0.001 | 1.8288 | 2.364  | 28.56    |

**Observasi:** Semua model terbaik menggunakan `seq_length=7` dan `learning_rate=0.001`. MAPE bervariasi cukup tinggi (26%-59%), wajar untuk data UMKM dengan volatilitas tinggi.

### 7.5 Format File Model
- **Bobot model:** `.h5` (Keras HDF5 format) — di-load dengan `tf.keras.models.load_model(path, compile=False)`
- **Scaler:** `.pkl` (joblib dump) — di-load dengan `joblib.load(path)`
- **Lokasi:** File model dan scaler tersimpan di `model/` directory

---

## 8. Konfigurasi & Environment

| Konfigurasi       | Nilai / Lokasi                              | Keterangan                    |
|-------------------|---------------------------------------------|-------------------------------|
| Database URL      | `mysql+pymysql://root:@localhost/dss_mie_ayam` | MySQL tanpa password (dev)   |
| JWT Secret Key    | `rahasia_dss_mi_ayam` (di `.env`)           | Kunci rahasia signing token   |
| JWT Algorithm     | `HS256`                                     | Algoritma enkripsi JWT        |
| JWT Expiry         | 24 jam                                      | Masa berlaku token            |
| Model Directory   | `model/`                                    | Path model + scaler           |
| Scheduler         | Cron jam 17:00 (5 PM)                       | Retrain otomatis              |
| API Prefix        | `/api`                                      | Semua endpoint di bawah /api  |

---

## 9. Dependencies (requirements.txt)

| Package              | Versi     | Fungsi                                    |
|----------------------|-----------|-------------------------------------------|
| fastapi              | >=0.100.0 | Web framework REST API                    |
| uvicorn[standard]    | >=0.22.0  | ASGI server                               |
| python-multipart     | >=0.0.6   | File upload (multipart form)              |
| pandas               | >=2.0.0   | Baca Excel, manipulasi data               |
| SQLAlchemy           | >=2.0.0   | ORM database                              |
| pymysql              | >=1.1.0   | Driver MySQL                              |
| bcrypt               | >=4.1.0   | Hashing & verifikasi password             |
| alembic              | >=1.11.0  | Database migration (belum dikonfigurasi)  |
| openpyxl             | >=3.1.0   | Engine baca file .xlsx                    |
| tensorflow           | >=2.13.0  | LSTM inference & training                 |
| scikit-learn         | >=1.3.0   | MinMaxScaler, metrik evaluasi             |
| python-dotenv        | >=1.0.0   | Load file .env                            |
| PyJWT                | >=2.8.0   | Enkode/dekode JWT token                   |
| apscheduler          | (tersirat)| Background job scheduling                 |
| joblib               | (tersirat)| Load/save scaler (.pkl)                   |

---

## 10. Isu & Catatan Teknis

### Yang Sudah Berfungsi
- Login JWT dan autentikasi dasar
- Upload data Excel dengan upsert
- Dashboard analytics (KPI, trend, komposisi)
- Load model LSTM untuk prediksi
- Scheduling retrain harian

### Yang Perlu Diperhatikan
1. **Auth belum diterapkan:** Endpoint login ada, tapi tidak ada middleware/guard yang mewajibkan token di endpoint lain.
2. **Harga menu duplikat:** Konstanta `HARGA_MENU` didefinisikan dua kali di `upload.py` dan `predict.py` — sebaiknya dipusatkan.
3. **Retraining masih stub:** Fungsi `retrain_lstm_model()` hanya placeholder, belum ada logika training aktual.
4. **Alembic belum dikonfigurasi:** `alembic.ini` kosong, tidak ada migration scripts.
5. **Database tanpa password:** Koneksi MySQL pakai `root@localhost` tanpa password — hanya untuk development.
6. **Model location mismatch:** Notebook save model ke `../app/ml_models/`, runtime load dari `model/`.
7. **Tidak ada frontend:** Codebase hanya berisi backend. Belum ada kode frontend di repository.
8. **File `=2.8.0`:** Artifact tidak sengaja dari perintah `pip install` yang salah redirect output.
9. **Global variable `is_data_uploaded_today`:** State di memori akan reset setiap server restart.
10. **MAPE tinggi:** Model LSTM memiliki MAPE 26-59%, menunjukkan prediksi kurang akurat untuk data dengan volatilitas tinggi.

---

## 11. Cara Menjalankan

```bash
# 1. Buat virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup database MySQL
# Buat database 'dss_mie_ayam' di MySQL

# 4. Buat user admin
python create_user.py

# 5. Jalankan server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server berjalan di `http://localhost:8000`. API docs (Swagger) tersedia di `http://localhost:8000/docs`.

---

## 12. Konteks Penggunaan sebagai LLM Context

Dokumen ini dirancang sebagai context injection untuk LLM agar dapat:
- Memahami arsitektur lengkap sistem DSS ini
- Mengetahui struktur database dan relasi antar tabel
- Memahami alur data dari upload → storage → prediksi → output
- Mengetahui format file model dan cara load-nya
- Mengidentifikasi isu teknis yang perlu diperbaiki
- Membantu dalam debugging, pengembangan fitur baru, atau refactor kode

**Endpoint yang tersedia:**
```
GET  /                          → Health check
POST /api/login                 → Login (username, password)
POST /api/upload-harian         → Upload Excel penjualan
GET  /api/kpi                   → KPI 7 hari
GET  /api/omzet-trend           → Tren omzet 7 hari
GET  /api/menu-composition      → Komposisi menu top 5
GET  /api/predict-omzet         → Prediksi omzet besok (LSTM)
GET  /api/train-status          → Status model
POST /api/retrain-manual        → Retrain manual
```
