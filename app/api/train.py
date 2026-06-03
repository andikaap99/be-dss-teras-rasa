from fastapi import APIRouter, BackgroundTasks
from app.services.trainer import retrain_lstm_model, get_last_trained_time

router = APIRouter()

@router.get("/train-status")
def get_train_status():
    """Endpoint untuk menampilkan tanggal & jam terakhir train di UI"""
    last_trained = get_last_trained_time()
    return {
        "status": "Ready",
        "terakhir_train": last_trained
    }

@router.post("/retrain-manual")
def trigger_manual_retrain(background_tasks: BackgroundTasks):
    """Endpoint untuk tombol retrain manual"""
    # Masukkan proses ke background task
    background_tasks.add_task(retrain_lstm_model)
    
    return {
        "message": "Proses training manual sedang berjalan di latar belakang."
    }