from fastapi import FastAPI
from app.database.database import engine
from app.models import user, sales
from app.api import auth, upload, analytics, predict
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.trainer import retrain_lstm_model
from app.api import train


user.Base.metadata.create_all(bind=engine)
sales.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    # Jadwal otomatis jam 17:00 tetap berjalan
    scheduler.add_job(retrain_lstm_model, 'cron', hour=17, minute=0)
    scheduler.start()
    
    yield
    
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(upload.router, prefix="/api", tags=["Data Sales"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics Data"])
app.include_router(predict.router, prefix="/api", tags=["Prediksi"])
app.include_router(train.router, prefix="/api", tags=["Model Training"])

@app.get("/")
def read_root():
    return {"message": "Website Online!"}
