import numpy as np
import tensorflow as tf
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.sales import Sales

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Load Model LSTM (dilakukan di luar endpoint agar tidak load ulang berkali-kali)
# Sesuaikan path ini dengan lokasi file modelmu
MODEL_PATH = "app/ml_models/lstm_omzet_model.h5" 
try:
    lstm_model = tf.keras.models.load_model(MODEL_PATH)
except Exception as e:
    lstm_model = None
    print(f"Gagal memuat model LSTM: {e}")

@router.get("/predict-omzet")
def predict_omzet(db: Session = Depends(get_db)):
    if lstm_model is None:
        raise HTTPException(status_code=500, detail="Model LSTM tidak tersedia di server.")

    hari_ini = date.today()

    # 2. Validasi: Cek apakah data hari ini sudah di-upload
    cek_hari_ini = db.query(Sales).filter(Sales.date == hari_ini).first()
    if not cek_hari_ini:
        raise HTTPException(
            status_code=400, 
            detail="Harap upload data penjualan hari ini terlebih dahulu untuk melakukan prediksi besok."
        )

    # 3. Ambil data historis untuk input LSTM
    # ASUMSI: Modelmu butuh data 7 hari terakhir (sequence_length = 7) untuk memprediksi besok.
    # Ubah angka 7 ini sesuai dengan input shape modelmu saat proses training!
    SEQ_LENGTH = 7 
    
    last_sales = db.query(Sales.omzet).order_by(Sales.date.desc()).limit(SEQ_LENGTH).all()
    
    if len(last_sales) < SEQ_LENGTH:
        raise HTTPException(
            status_code=400, 
            detail=f"Data belum cukup. Model membutuhkan minimal {SEQ_LENGTH} hari data historis."
        )

    # 4. Preprocessing Data
    # Kita harus membalik urutannya karena query sebelumnya descending (hari ini -> 7 hari lalu)
    # Sedangkan LSTM butuh urutan kronologis (7 hari lalu -> hari ini)
    sales_data = [sale.omzet for sale in reversed(last_sales)]

    # CATATAN PENTING: 
    # Jika saat training datamu di-scaling (misal pakai MinMaxScaler), 
    # kamu WAJIB melakukan scaling yang sama pada 'sales_data' di baris ini sebelum di-reshape.

    # Reshape input sesuai format LSTM (batch_size, time_steps, features) -> (1, 7, 1)
    input_data = np.array(sales_data).reshape(1, SEQ_LENGTH, 1)

    # 5. Lakukan Prediksi
    try:
        prediction = lstm_model.predict(input_data)
        
        # Ambil nilai prediksinya (Jika pakai scaler, lakukan inverse_transform di sini)
        predicted_omzet = float(prediction[0][0])
        
        tanggal_besok = hari_ini + timedelta(days=1)

        return {
            "message": "Prediksi berhasil",
            "tanggal_prediksi": str(tanggal_besok),
            "estimasi_omzet": int(predicted_omzet)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saat melakukan prediksi: {str(e)}")