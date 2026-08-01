import os
import json
import time
import numpy as np
import joblib
import tensorflow as tf
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from app.database.database import SessionLocal
from app.models.sales import Menu, Transaction

MODEL_DIR = "model"

MENUS = ["mie_ayam", "alpukat", "mangga", "jeruk", "jambu", "strobery"]

MENU_CONFIG = {
    "mie_ayam": {"lstm_units": 64, "learning_rate": 0.001},
    "alpukat": {"lstm_units": 64, "learning_rate": 0.001},
    "mangga": {"lstm_units": 128, "learning_rate": 0.001},
    "jeruk": {"lstm_units": 32, "learning_rate": 0.001},
    "jambu": {"lstm_units": 32, "learning_rate": 0.001},
    "strobery": {"lstm_units": 128, "learning_rate": 0.001},
}

SEQ_LENGTH = 7


def retrain_lstm_model():
    print("Memulai proses training ulang model LSTM...")
    start_time = time.time()
    try:
        db = SessionLocal()

        menu_id_map = {}
        for m in db.query(Menu).all():
            menu_id_map[m.name] = m.id

        dates = [row[0] for row in db.query(Transaction.date).distinct().order_by(Transaction.date.asc()).all()]

        if len(dates) < SEQ_LENGTH + 5:
            print(f"Data tidak cukup untuk training ({len(dates)} hari). Minimal {SEQ_LENGTH + 5} hari.")
            db.close()
            return

        all_values = np.zeros((len(dates), len(MENUS)), dtype=float)
        for i, d in enumerate(dates):
            for j, menu_name in enumerate(MENUS):
                menu_id = menu_id_map.get(menu_name)
                if menu_id:
                    tx = db.query(Transaction.quantity).filter(Transaction.date == d, Transaction.menu_id == menu_id).first()
                    if tx:
                        all_values[i, j] = tx[0]

        db.close()

        metrics_summary = {
            "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_range": {
                "start": str(dates[0]),
                "end": str(dates[-1]),
                "total_days": len(dates),
            },
            "menus": {},
        }

        for menu_idx, menu_name in enumerate(MENUS):
            print(f"Training model {menu_name}...")
            menu_values = all_values[:, menu_idx].reshape(-1, 1)

            scaler = MinMaxScaler()
            scaled = scaler.fit_transform(menu_values)

            X, y = [], []
            for i in range(SEQ_LENGTH, len(scaled)):
                X.append(scaled[i - SEQ_LENGTH : i, 0])
                y.append(scaled[i, 0])
            X = np.array(X)
            y = np.array(y)
            X = X.reshape(X.shape[0], X.shape[1], 1)

            config = MENU_CONFIG[menu_name]
            model = tf.keras.Sequential(
                [
                    tf.keras.layers.LSTM(config["lstm_units"], input_shape=(SEQ_LENGTH, 1)),
                    tf.keras.layers.Dense(1),
                ]
            )
            model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=config["learning_rate"]),
                loss="mse",
            )

            model.fit(X, y, epochs=50, batch_size=8, verbose=0)

            predictions = model.predict(X, verbose=0)
            pred_inv = scaler.inverse_transform(predictions).flatten()
            y_inv = scaler.inverse_transform(y.reshape(-1, 1)).flatten()

            mae = float(np.mean(np.abs(pred_inv - y_inv)))
            rmse = float(np.sqrt(np.mean((pred_inv - y_inv) ** 2)))
            non_zero = y_inv != 0
            if non_zero.any():
                mape = float(np.mean(np.abs((y_inv[non_zero] - pred_inv[non_zero]) / y_inv[non_zero])) * 100)
            else:
                mape = 0.0

            model_path = os.path.join(MODEL_DIR, f"{menu_name}_lstm_model.h5")
            scaler_path = os.path.join(MODEL_DIR, f"{menu_name}_scaler.pkl")
            model.save(model_path)
            joblib.dump(scaler, scaler_path)

            metrics_summary["menus"][menu_name] = {
                "model_file": f"{menu_name}_lstm_model.h5",
                "scaler_file": f"{menu_name}_scaler.pkl",
                "best_params": {
                    "seq_length": SEQ_LENGTH,
                    "lstm_units": config["lstm_units"],
                    "learning_rate": config["learning_rate"],
                },
                "metrics": {
                    "seq_length": SEQ_LENGTH,
                    "lstm_units": config["lstm_units"],
                    "learning_rate": config["learning_rate"],
                    "MAE": round(mae, 4),
                    "RMSE": round(rmse, 4),
                    "MAPE": round(mape, 2),
                },
            }
            print(f"  {menu_name} selesai | MAE={mae:.4f} RMSE={rmse:.4f} MAPE={mape:.2f}%")

        metadata_path = os.path.join(MODEL_DIR, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metrics_summary, f, indent=2)

        elapsed = round(time.time() - start_time, 2)
        print(f"Training selesai dalam {elapsed} detik. Semua model berhasil diperbarui.")
    except Exception as e:
        print(f"Error saat training: {e}")


def get_last_trained_time():
    latest_time = None
    for menu in MENUS:
        model_path = os.path.join(MODEL_DIR, f"{menu}_lstm_model.h5")
        if os.path.exists(model_path):
            mtime = os.path.getmtime(model_path)
            dt = datetime.fromtimestamp(mtime)
            if latest_time is None or dt > latest_time:
                latest_time = dt
    if latest_time:
        return latest_time.strftime("%Y-%m-%d %H:%M:%S")
    return "Belum pernah di-train"
