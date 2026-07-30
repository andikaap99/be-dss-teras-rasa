### 1. Authentication
#### Login (Dapatkan Token)
Endpoint ini digunakan untuk menukar kredensial (username & password) dengan *access_token* JWT. Token ini nantinya wajib disematkan pada Header saat ingin mengakses fitur prediksi atau fitur tertutup lainnya.
- URL: /api/login
- Method: POST
- Format Body: application/json

**Request Body**
| Key      | Tipe   | Wajib? | Keterangan                       |
|----------|--------|--------|----------------------------------|
| username | String | Ya     | Username user                    |
| password | String | Ya     | Password user                    |

**Contoh Request (Javascript/Axios)**
```
const payload = {
  username: 'admin',
  password: 'dikaganteng123'
};

axios.post('/api/login', payload, {
  headers: { 'Content-Type': 'application/json' }
});
```

**Response Sukses (200 OK)**
```
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "message": "Login berhasil"
}
```

### 2. Data Sales
#### Upload Data Harian
Endpoint ini digunakan untuk mengunggah file Excel (.xlsx atau .xls) yang berisi rekap transaksi penjualan. Jika tanggal yang sama sudah ada di database, sistem akan otomatis menimpanya (replace/update) dengan data terbaru dari file.
- URL: /api/upload-harian
- Method: POST
- Format Body: multipart/form-data

**Request Body (JSON)**
| Key       | Tipe   | Wajib? | Keterangan                  |
|-----------|--------|--------|-----------------------------|
| file      | file   | Ya     | File rekap penjualan (.xlsx / .xls)|

**Format Kolom Excel:**
| Kolom     | Tipe   | Keterangan                  |
|-----------|--------|-----------------------------|
| date      | Date   | Tanggal penjualan (format: YYYY-MM-DD) |
| mie ayam  | Number | Jumlah porsi mie ayam terjual |
| alpukat   | Number | Jumlah porsi jus alpukat terjual |
| mangga    | Number | Jumlah porsi jus mangga terjual |
| jeruk     | Number | Jumlah porsi jus jeruk terjual |
| jambu     | Number | Jumlah porsi jus jambu terjual |
| strobery  | Number | Jumlah porsi jus strobery terjual |

**Contoh Request (Javascript/Axios)**
```
// Asumsi 'fileInput' adalah elemen <input type="file"> di HTML
const file = fileInput.files[0]; 
const formData = new FormData();
formData.append('file', file);

axios.post('/api/upload-harian', formData, {
  headers: { 
    'Content-Type': 'multipart/form-data'
    // 'Authorization': `Bearer ${token}` <-- (Opsional, jika endpoint ini mau diproteksi nantinya)
  }
});
```

**Response Sukses (200 OK)**
```
{
  "message": "Data berhasil disimpan/diperbarui",
  "status_hari_ini": true
}
```

### 3. Dashboard Analytics
#### Get KPI (Ringkasan Performa)
Endpoint ini digunakan untuk mendapatkan ringkasan angka performa penjualan selama 7 hari terakhir, mencakup total porsi mie ayam serta informasi jus yang paling banyak dan paling sedikit terjual.

- URL: /api/kpi

- Method: GET

- Format Body: N/A (Tidak membutuhkan body)

**Contoh Request (Javascript/Axios)**
```
axios.get('/api/kpi', {
  headers: { 
    // 'Authorization': `Bearer ${token}` 
  }
});
```

**Response Sukses (200 OK)**
```
{
  "kpi": {
    "total_penjualan_mie_ayam": 125,
    "jus_terlaris": "Mangga",
    "jus_tersepi": "Strobery"
  }
}
```
#### Get Omzet Trend (Line Chart)
Endpoint ini digunakan untuk mengambil data tren omzet harian selama 7 hari terakhir. Data dikirim dalam dua array terpisah (labels dan data) untuk memudahkan pemetaan pada grafik garis (misal: Chart.js).

- URL: /api/omzet-trend

- Method: GET

- Format Body: N/A

**Contoh Request (Javascript/Axios)**
```
axios.get('/api/omzet-trend');
```

**Response Sukses (200 OK)**
```
{
  "labels": ["2026-05-07", "2026-05-08", "2026-05-09", "2026-05-10", "2026-05-11", "2026-05-12", "2026-05-13"],
  "data": [150000, 200000, 185000, 210000, 190000, 225000, 240000]
}
```
#### Get Menu Composition (Pie Chart)
Endpoint ini digunakan untuk mendapatkan komposisi penjualan dari 5 menu dengan porsi tertinggi selama 7 hari terakhir. Cocok digunakan untuk visualisasi grafik pie atau donat.

- URL: /api/menu-composition

- Method: GET

- Format Body: N/A

**Contoh Request (Javascript/Axios)**
```
axios.get('/api/menu-composition');
```

**Response Sukses (200 OK)**
```
{
  "labels": ["Mie Ayam", "Mangga", "Alpukat", "Jeruk", "Jambu"],
  "data": [125, 45, 30, 25, 15]
}
```

### 4. Prediksi & Training
#### Prediksi Omzet Besok
Endpoint ini digunakan untuk memprediksi estimasi omzet penjualan hari berikutnya. Sistem akan menggunakan model LSTM yang sudah di-training sebelumnya untuk setiap menu (Mie Ayam, Alpukat, Mangga, Jeruk, Jambu, Strobery) dan mengalikan hasil prediksi porsi dengan harga satuan masing-masing menu.
- URL: /api/predict-omzet
- Method: GET
- Format Body: N/A

**Catatan Penting:**
- Data penjualan hari ini harus sudah di-upload terlebih dahulu sebelum melakukan prediksi.
- Minimal harus ada 7 hari data historis di database.

**Contoh Request (Javascript/Axios)**
```
axios.get('/api/predict-omzet');
```

**Response Sukses (200 OK)**
```
{
  "message": "Prediksi berhasil",
  "tanggal_prediksi": "2026-07-23",
  "estimasi_omzet": 285000,
  "detail_per_menu": {
    "mie_ayam": { "porsi": 12, "harga_satuan": 15000, "omzet": 180000 },
    "alpukat": { "porsi": 3, "harga_satuan": 12000, "omzet": 36000 },
    "mangga": { "porsi": 2, "harga_satuan": 12000, "omzet": 24000 },
    "jeruk": { "porsi": 2, "harga_satuan": 10000, "omzet": 20000 },
    "jambu": { "porsi": 1, "harga_satuan": 10000, "omzet": 10000 },
    "strobery": { "porsi": 1, "harga_satuan": 12000, "omzet": 15000 }
  }
}
```

#### Status Training Model
Endpoint ini digunakan untuk menampilkan status kesiapan model dan waktu terakhir model di-training.
- URL: /api/train-status
- Method: GET

**Contoh Request**
```
axios.get('/api/train-status');
```

**Response Sukses (200 OK)**
```
{
  "status": "Ready",
  "terakhir_train": "2026-07-22 17:00:00"
}
```

#### Retrain Manual
Endpoint ini digunakan untuk menjalankan proses training ulang model secara manual di latar belakang.
- URL: /api/retrain-manual
- Method: POST

**Contoh Request**
```
axios.post('/api/retrain-manual');
```

**Response Sukses (200 OK)**
```
{
  "message": "Proses training manual sedang berjalan di latar belakang."
}
```

#### Prediksi Kebutuhan Bahan Baku
Endpoint ini digunakan untuk memprediksi kebutuhan bahan baku besok berdasarkan hasil prediksi porsi penjualan per menu. Sistem mengalikan prediksi porsi dengan kamus bahan baku untuk setiap menu, lalu menjumlahkan seluruh kebutuhan bahan baku.

- URL: /api/predict-bahan-baku
- Method: GET
- Format Body: N/A

**Catatan Penting:**
- Data penjualan hari ini harus sudah di-upload terlebih dahulu sebelum melakukan prediksi.
- Minimal harus ada 7 hari data historis di database.

**Contoh Request (Javascript/Axios)**
```
axios.get('/api/predict-bahan-baku');
```

**Response Sukses (200 OK)**
```json
{
  "message": "Prediksi kebutuhan bahan baku berhasil",
  "tanggal_prediksi": "2026-07-31",
  "prediksi_porsi_per_menu": {
    "mie_ayam": 45,
    "alpukat": 10,
    "mangga": 8,
    "jeruk": 7,
    "jambu": 5,
    "strobery": 9
  },
  "kebutuhan_bahan_baku": [
    { "nama": "Mie basah", "jumlah": 4500, "satuan": "gram" },
    { "nama": "Daging ayam (cincang/dadu)", "jumlah": 3825, "satuan": "gram" },
    { "nama": "Minyak ayam/bawang", "jumlah": 675, "satuan": "ml" },
    { "nama": "Kecap asin", "jumlah": 225, "satuan": "ml" },
    { "nama": "Kecap manis", "jumlah": 810, "satuan": "ml" },
    { "nama": "Saus tiram", "jumlah": 225, "satuan": "gram" },
    { "nama": "Garam", "jumlah": 112.5, "satuan": "gram" },
    { "nama": "Kaldu bubuk", "jumlah": 112.5, "satuan": "gram" },
    { "nama": "Merica bubuk", "jumlah": 45, "satuan": "gram" },
    { "nama": "Bawang putih (halus)", "jumlah": 292.5, "satuan": "gram" },
    { "nama": "Bawang merah (halus)", "jumlah": 405, "satuan": "gram" },
    { "nama": "Air/Kuah kaldu", "jumlah": 7875, "satuan": "ml" },
    { "nama": "Daging Alpukat", "jumlah": 1100, "satuan": "gram" },
    { "nama": "Gula Pasir", "jumlah": 673.75, "satuan": "gram" },
    { "nama": "Susu Kental Manis", "jumlah": 300, "satuan": "ml" },
    { "nama": "Air Matang / Es Batu", "jumlah": 2625, "satuan": "ml" },
    { "nama": "Daging Mangga", "jumlah": 880, "satuan": "gram" },
    { "nama": "Susu Kental Manis / UHT", "jumlah": 340, "satuan": "ml" },
    { "nama": "Air Perasan Jeruk", "jumlah": 770, "satuan": "ml" },
    { "nama": "Daging Jambu Biji Merah", "jumlah": 550, "satuan": "gram" },
    { "nama": "Buah Stroberi Segar", "jumlah": 810, "satuan": "gram" }
  ]
}
```


