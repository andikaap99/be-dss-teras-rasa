import os
import joblib
import numpy as np
import tensorflow as tf
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.sales import Sales

router = APIRouter()

MODEL_DIR = "model"

MENUS = ["mie_ayam", "alpukat", "mangga", "jeruk", "jambu", "strobery"]

HARGA_MENU = {
    "mie_ayam": 15000,
    "alpukat": 12000,
    "mangga": 12000,
    "jeruk": 10000,
    "jambu": 10000,
    "strobery": 12000
}

SEQ_LENGTH = 7

KAMUS_BAHAN_BAKU = {
    "mie_ayam": [
        {"nama": "Mie basah", "jumlah": 100, "satuan": "gram"},
        {"nama": "Daging ayam (cincang/dadu)", "jumlah": 85, "satuan": "gram"},
        {"nama": "Minyak ayam/bawang", "jumlah": 15, "satuan": "ml"},
        {"nama": "Kecap asin", "jumlah": 5, "satuan": "ml"},
        {"nama": "Kecap manis", "jumlah": 18, "satuan": "ml"},
        {"nama": "Saus tiram", "jumlah": 5, "satuan": "gram"},
        {"nama": "Garam", "jumlah": 2.5, "satuan": "gram"},
        {"nama": "Kaldu bubuk", "jumlah": 2.5, "satuan": "gram"},
        {"nama": "Merica bubuk", "jumlah": 1, "satuan": "gram"},
        {"nama": "Bawang putih (halus)", "jumlah": 6.5, "satuan": "gram"},
        {"nama": "Bawang merah (halus)", "jumlah": 9, "satuan": "gram"},
        {"nama": "Air/Kuah kaldu", "jumlah": 175, "satuan": "ml"},
    ],
    "alpukat": [
        {"nama": "Daging Alpukat", "jumlah": 110, "satuan": "gram"},
        {"nama": "Gula Pasir", "jumlah": 17.5, "satuan": "gram"},
        {"nama": "Susu Kental Manis", "jumlah": 30, "satuan": "ml"},
        {"nama": "Air Matang / Es Batu", "jumlah": 125, "satuan": "ml"},
    ],
    "mangga": [
        {"nama": "Daging Mangga", "jumlah": 110, "satuan": "gram"},
        {"nama": "Gula Pasir", "jumlah": 15, "satuan": "gram"},
        {"nama": "Susu Kental Manis / UHT", "jumlah": 15, "satuan": "ml"},
        {"nama": "Air Matang / Es Batu", "jumlah": 150, "satuan": "ml"},
    ],
    "jeruk": [
        {"nama": "Air Perasan Jeruk", "jumlah": 110, "satuan": "ml"},
        {"nama": "Gula Pasir", "jumlah": 22.5, "satuan": "gram"},
        {"nama": "Air Matang / Es Batu", "jumlah": 100, "satuan": "ml"},
    ],
    "jambu": [
        {"nama": "Daging Jambu Biji Merah", "jumlah": 110, "satuan": "gram"},
        {"nama": "Gula Pasir", "jumlah": 20, "satuan": "gram"},
        {"nama": "Susu Kental Manis / UHT", "jumlah": 15, "satuan": "ml"},
        {"nama": "Air Matang / Es Batu", "jumlah": 175, "satuan": "ml"},
    ],
    "strobery": [
        {"nama": "Buah Stroberi Segar", "jumlah": 90, "satuan": "gram"},
        {"nama": "Gula Pasir", "jumlah": 22.5, "satuan": "gram"},
        {"nama": "Susu Kental Manis / UHT", "jumlah": 20, "satuan": "ml"},
        {"nama": "Air Matang / Es Batu", "jumlah": 125, "satuan": "ml"},
    ],
}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def load_models():
    models = {}
    for menu in MENUS:
        model_path = os.path.join(MODEL_DIR, f"{menu}_lstm_model.h5")
        scaler_path = os.path.join(MODEL_DIR, f"{menu}_scaler.pkl")
        try:
            model = tf.keras.models.load_model(model_path, compile=False)
            scaler = joblib.load(scaler_path)
            models[menu] = {"model": model, "scaler": scaler}
        except Exception as e:
            print(f"Gagal load model {menu}: {e}")
            models[menu] = None
    return models

lstm_models = load_models()

@router.get("/predict-omzet")
def predict_omzet(db: Session = Depends(get_db)):
    hari_ini = date.today()

    cek_hari_ini = db.query(Sales).filter(Sales.date == hari_ini).first()
    if not cek_hari_ini:
        raise HTTPException(
            status_code=400,
            detail="Harap upload data penjualan hari ini terlebih dahulu untuk melakukan prediksi besok."
        )

    all_loaded = all(v is not None for v in lstm_models.values())
    if not all_loaded:
        raise HTTPException(status_code=500, detail="Beberapa model LSTM belum tersedia di server.")

    last_sales = db.query(Sales).order_by(Sales.date.desc()).limit(SEQ_LENGTH).all()

    if len(last_sales) < SEQ_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Data belum cukup. Model membutuhkan minimal {SEQ_LENGTH} hari data historis."
        )

    last_sales.reverse()

    prediksi_per_menu = {}
    total_omzet = 0

    for menu in MENUS:
        raw_data = [getattr(sale, menu) for sale in last_sales]
        scaled_data = lstm_models[menu]["scaler"].transform(np.array(raw_data).reshape(-1, 1))
        input_data = scaled_data.reshape(1, SEQ_LENGTH, 1)

        prediction = lstm_models[menu]["model"].predict(input_data)
        predicted_porsi = lstm_models[menu]["scaler"].inverse_transform(prediction)[0][0]
        predicted_porsi = max(0, int(round(predicted_porsi)))

        omzet_menu = predicted_porsi * HARGA_MENU[menu]
        total_omzet += omzet_menu

        prediksi_per_menu[menu] = {
            "porsi": predicted_porsi,
            "harga_satuan": HARGA_MENU[menu],
            "omzet": omzet_menu
        }

    tanggal_besok = hari_ini + timedelta(days=1)

    return {
        "message": "Prediksi berhasil",
        "tanggal_prediksi": str(tanggal_besok),
        "estimasi_omzet": total_omzet,
        "detail_per_menu": prediksi_per_menu
    }

@router.get("/predict-bahan-baku")
def predict_bahan_baku(db: Session = Depends(get_db)):
    hari_ini = date.today()

    cek_hari_ini = db.query(Sales).filter(Sales.date == hari_ini).first()
    if not cek_hari_ini:
        raise HTTPException(
            status_code=400,
            detail="Harap upload data penjualan hari ini terlebih dahulu untuk melakukan prediksi besok."
        )

    all_loaded = all(v is not None for v in lstm_models.values())
    if not all_loaded:
        raise HTTPException(status_code=500, detail="Beberapa model LSTM belum tersedia di server.")

    last_sales = db.query(Sales).order_by(Sales.date.desc()).limit(SEQ_LENGTH).all()

    if len(last_sales) < SEQ_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Data belum cukup. Model membutuhkan minimal {SEQ_LENGTH} hari data historis."
        )

    last_sales.reverse()

    prediksi_porsi = {}
    for menu in MENUS:
        raw_data = [getattr(sale, menu) for sale in last_sales]
        scaled_data = lstm_models[menu]["scaler"].transform(np.array(raw_data).reshape(-1, 1))
        input_data = scaled_data.reshape(1, SEQ_LENGTH, 1)
        prediction = lstm_models[menu]["model"].predict(input_data)
        predicted_porsi = lstm_models[menu]["scaler"].inverse_transform(prediction)[0][0]
        prediksi_porsi[menu] = max(0, int(round(predicted_porsi)))

    total_bahan = {}
    for menu, porsi in prediksi_porsi.items():
        if porsi <= 0:
            continue
        for bahan in KAMUS_BAHAN_BAKU.get(menu, []):
            key = bahan["nama"]
            if key not in total_bahan:
                total_bahan[key] = {"nama": bahan["nama"], "jumlah": 0, "satuan": bahan["satuan"]}
            total_bahan[key]["jumlah"] += bahan["jumlah"] * porsi

    for item in total_bahan.values():
        item["jumlah"] = round(item["jumlah"], 2)

    tanggal_besok = hari_ini + timedelta(days=1)

    return {
        "message": "Prediksi kebutuhan bahan baku berhasil",
        "tanggal_prediksi": str(tanggal_besok),
        "prediksi_porsi_per_menu": prediksi_porsi,
        "kebutuhan_bahan_baku": list(total_bahan.values())
    }
