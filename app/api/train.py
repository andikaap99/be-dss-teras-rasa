from fastapi import APIRouter, BackgroundTasks, Depends
from app.services.trainer import retrain_lstm_model, get_last_trained_time
from app.core.deps import get_current_user

router = APIRouter()


@router.get("/train-status")
def get_train_status(current_user=Depends(get_current_user)):
    last_trained = get_last_trained_time()
    return {
        "status": "Ready",
        "terakhir_train": last_trained,
    }


@router.post("/retrain-manual")
def trigger_manual_retrain(
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
):
    background_tasks.add_task(retrain_lstm_model)

    return {
        "message": "Proses training manual sedang berjalan di latar belakang.",
    }
