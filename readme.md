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


