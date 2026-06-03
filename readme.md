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
### 4. Dashboard Prediksi & Retrain Model
**Get Prediksi Omzet Esok Hari**
Endpoint ini digunakan untuk memprediksi estimasi omzet penjualan untuk esok hari menggunakan model Machine Learning (LSTM). Sistem akan memvalidasi terlebih dahulu apakah data penjualan hari ini sudah diunggah atau belum.

- URL: /api/predict-omzet

- Method: GET

- Format Body: N/A (Tidak membutuhkan body)

**Contoh Request (Javascript/Axios)**
```
axios.get('/api/predict-omzet', {
  headers: { 
    // 'Authorization': `Bearer ${token}` 
  }
});
```

**Response Sukses (200 OK)**
```
{
  "message": "Prediksi berhasil",
  "tanggal_prediksi": "2026-06-04",
  "estimasi_omzet": 255000
}
```
**Get Status Training Model**
Endpoint ini digunakan untuk menampilkan tanggal dan jam berapa model LSTM terakhir kali dilatih (berdasarkan waktu modifikasi file model .h5 di server).

- URL: /api/train-status

- Method: GET

- Format Body: N/A

**Contoh Request (Javascript/Axios)**
```
axios.get('/api/train-status', {
  headers: { 
    // 'Authorization': `Bearer ${token}` 
  }
});
```

**Response Sukses (200 OK)**
```
{
  "status": "Ready",
  "terakhir_train": "2026-06-02 17:00:05"
}
```
**Get Retrain Model (Manual)**
Endpoint ini digunakan untuk memicu proses training ulang model LSTM secara manual di luar jadwal otomatis. Proses berjalan sebagai background task sehingga langsung memberikan response tanpa membuat halaman menunggu (loading) lama.

- URL: /api/retrain-manual

- Method: POST

- Format Body: N/A

**Contoh Request (Javascript/Axios)**
```
axios.post('/api/retrain-manual', {}, {
  headers: { 
    // 'Authorization': `Bearer ${token}` 
  }
});
```

**Response Sukses (200 OK)**
```
{
  "message": "Proses training manual sedang berjalan di latar belakang."
}
```


