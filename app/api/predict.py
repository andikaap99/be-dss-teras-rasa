import os
import joblib
import numpy as np
import tensorflow as tf
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.sales import Menu, Ingredient, MenuIngredient, Transaction

router = APIRouter()

MODEL_DIR = "model"

MENUS = ["mie_ayam", "alpukat", "mangga", "jeruk", "jambu", "strobery"]

HARGA_MENU = {
    "mie_ayam": 15000,
    "alpukat": 12000,
    "mangga": 12000,
    "jeruk": 10000,
    "jambu": 10000,
    "strobery": 12000,
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


def get_menu_id_map(db: Session):
    return {m.name: m.id for m in db.query(Menu).all()}


def get_predicted_porsi(db: Session):
    hari_ini = date.today()

    cek_hari_ini = db.query(Transaction).filter(Transaction.date == hari_ini).first()
    if not cek_hari_ini:
        raise HTTPException(
            status_code=400,
            detail="Harap upload data penjualan hari ini terlebih dahulu untuk melakukan prediksi besok.",
        )

    all_loaded = all(v is not None for v in lstm_models.values())
    if not all_loaded:
        raise HTTPException(status_code=500, detail="Beberapa model LSTM belum tersedia di server.")

    menu_id_map = get_menu_id_map(db)

    last_dates = (
        db.query(Transaction.date)
        .distinct()
        .order_by(Transaction.date.desc())
        .limit(SEQ_LENGTH)
        .all()
    )

    if len(last_dates) < SEQ_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Data belum cukup. Model membutuhkan minimal {SEQ_LENGTH} hari data historis.",
        )

    dates_needed = [row[0] for row in last_dates]
    dates_needed.reverse()

    prediksi_porsi = {}
    for menu_name in MENUS:
        menu_id = menu_id_map.get(menu_name)
        if not menu_id:
            prediksi_porsi[menu_name] = 0
            continue

        daily_qty = []
        for d in dates_needed:
            tx = (
                db.query(Transaction.quantity)
                .filter(Transaction.date == d, Transaction.menu_id == menu_id)
                .first()
            )
            daily_qty.append(tx[0] if tx else 0)

        raw_data = np.array(daily_qty, dtype=float)
        scaled_data = lstm_models[menu_name]["scaler"].transform(raw_data.reshape(-1, 1))
        input_data = scaled_data.reshape(1, SEQ_LENGTH, 1)

        prediction = lstm_models[menu_name]["model"].predict(input_data)
        predicted_porsi = lstm_models[menu_name]["scaler"].inverse_transform(prediction)[0][0]
        prediksi_porsi[menu_name] = max(0, int(round(predicted_porsi)))

    return prediksi_porsi


@router.get("/predict-omzet")
def predict_omzet(db: Session = Depends(get_db)):
    prediksi_porsi = get_predicted_porsi(db)

    total_omzet = 0
    prediksi_per_menu = {}

    for menu_name, porsi in prediksi_porsi.items():
        harga = HARGA_MENU[menu_name]
        omzet_menu = porsi * harga
        total_omzet += omzet_menu
        prediksi_per_menu[menu_name] = {
            "porsi": porsi,
            "harga_satuan": harga,
            "omzet": omzet_menu,
        }

    tanggal_besok = date.today() + timedelta(days=1)

    return {
        "message": "Prediksi berhasil",
        "tanggal_prediksi": str(tanggal_besok),
        "estimasi_omzet": total_omzet,
        "detail_per_menu": prediksi_per_menu,
    }


@router.get("/predict-bahan-baku")
def predict_bahan_baku(db: Session = Depends(get_db)):
    prediksi_porsi = get_predicted_porsi(db)

    total_bahan = {}
    for menu_name, porsi in prediksi_porsi.items():
        if porsi <= 0:
            continue
        for bahan in KAMUS_BAHAN_BAKU.get(menu_name, []):
            key = bahan["nama"]
            if key not in total_bahan:
                total_bahan[key] = {"nama": bahan["nama"], "jumlah": 0, "satuan": bahan["satuan"]}
            total_bahan[key]["jumlah"] += bahan["jumlah"] * porsi

    for item in total_bahan.values():
        item["jumlah"] = round(item["jumlah"], 2)

    tanggal_besok = date.today() + timedelta(days=1)

    return {
        "message": "Prediksi kebutuhan bahan baku berhasil",
        "tanggal_prediksi": str(tanggal_besok),
        "prediksi_porsi_per_menu": prediksi_porsi,
        "kebutuhan_bahan_baku": list(total_bahan.values()),
    }
