import os
import time
from datetime import datetime

# Path file model
MODEL_PATH = "app/ml_models/lstm_omzet_model.h5"

def retrain_lstm_model():
    print("Memulai proses training ulang model LSTM...")
    try:
        # LOGIKA TRAINING DI SINI
        # 1. Ambil data dari DB
        # 2. Preprocessing
        # 3. lstm_model.fit(...)
        
        # Simulasi proses training (hapus baris ini nanti)
        time.sleep(5) 
        
        # 4. Simpan model (ini akan memperbarui waktu 'Modified' pada file OS)
        # lstm_model.save(MODEL_PATH)
        
        print("Training selesai dan model berhasil diperbarui.")
    except Exception as e:
        print(f"Error saat training: {e}")

def get_last_trained_time():
    """Mengambil waktu terakhir file model diperbarui dari sistem operasi"""
    if os.path.exists(MODEL_PATH):
        mtime = os.path.getmtime(MODEL_PATH)
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
    return "Belum pernah di-train"