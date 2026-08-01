import pandas as pd
import io
from datetime import date
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.sales import Menu, Transaction

router = APIRouter()

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

    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Format file harus Excel")

    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))

        menu_lookup = {}
        for menu in db.query(Menu).all():
            menu_lookup[menu.name] = menu

        EXCEL_TO_DB = {
            "mie ayam": "mie_ayam",
            "alpukat": "alpukat",
            "mangga": "mangga",
            "jeruk": "jeruk",
            "jambu": "jambu",
            "strobery": "strobery",
        }

        for index, row in df.iterrows():
            row_date = row["date"]
            if isinstance(row_date, pd.Timestamp):
                row_date = row_date.date()

            for excel_col, db_name in EXCEL_TO_DB.items():
                qty = int(row[excel_col])
                if qty <= 0:
                    continue

                menu = menu_lookup.get(db_name)
                if not menu:
                    continue

                total_price = qty * menu.price

                existing = (
                    db.query(Transaction)
                    .filter(Transaction.date == row_date, Transaction.menu_id == menu.id)
                    .first()
                )

                if existing:
                    existing.quantity = qty
                    existing.total_price = total_price
                else:
                    new_tx = Transaction(
                        date=row_date,
                        menu_id=menu.id,
                        quantity=qty,
                        total_price=total_price,
                    )
                    db.add(new_tx)

            if row_date == date.today():
                is_data_uploaded_today = True

        db.commit()
        return {
            "message": "Data berhasil disimpan/diperbarui",
            "status_hari_ini": is_data_uploaded_today,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan: {str(e)}")
