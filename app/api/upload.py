import pandas as pd
import io
from datetime import date
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.sales import Sales

router = APIRouter()

# Variabel global sesuai permintaan
is_data_uploaded_today = False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload-harian")
async def upload_harian(file: UploadFile = File(...), db: Session = Depends(get_db)):
    global is_data_uploaded_today
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Format file harus Excel")

    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Iterasi baris (mengantisipasi jika user upload > 1 baris sekaligus)
        for index, row in df.iterrows():
            row_date = row['date']
            if isinstance(row_date, pd.Timestamp):
                row_date = row_date.date()
                
            # Cek apakah tanggal sudah ada di DB
            db_sale = db.query(Sales).filter(Sales.date == row_date).first()
            
            if db_sale:
                # Replace/Update data jika sudah ada
                db_sale.mie_ayam = row['mie ayam']
                db_sale.alpukat = row['alpukat']
                db_sale.mangga = row['mangga']
                db_sale.jeruk = row['jeruk']
                db_sale.jambu = row['jambu']
                db_sale.strobery = row['strobery']
            else:
                # Insert data baru
                new_sale = Sales(
                    date=row_date,
                    mie_ayam=row['mie ayam'],
                    alpukat=row['alpukat'],
                    mangga=row['mangga'],
                    jeruk=row['jeruk'],
                    jambu=row['jambu'],
                    strobery=row['strobery']
                )
                db.add(new_sale)
                
            # Update variabel global jika tanggal di Excel = tanggal hari ini di server
            if row_date == date.today():
                is_data_uploaded_today = True

        db.commit()
        return {
            "message": "Data berhasil disimpan/diperbarui", 
            "status_hari_ini": is_data_uploaded_today
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan: {str(e)}")