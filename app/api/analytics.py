from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import SessionLocal
from app.models.sales import Sales

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/kpi")
def get_kpi(db: Session = Depends(get_db)):
    # 1. Buat subquery untuk mengambil 7 baris terakhir berdasarkan tanggal
    subq = db.query(Sales).order_by(Sales.date.desc()).limit(7).subquery()

    # 2. Query sum diarahkan ke kolom-kolom dari subquery tersebut (menggunakan .c)
    totals = db.query(
        func.sum(subq.c.mie_ayam).label('mie_ayam'),
        func.sum(subq.c.alpukat).label('alpukat'),
        func.sum(subq.c.mangga).label('mangga'),
        func.sum(subq.c.jeruk).label('jeruk'),
        func.sum(subq.c.jambu).label('jambu'),
        func.sum(subq.c.strobery).label('strobery')
    ).first()

    # 3. Handle jika database masih kosong
    if not totals or totals.mie_ayam is None:
        return {"kpi": {"total_penjualan_mie_ayam": 0, "jus_terlaris": "-", "jus_tersepi": "-"}}

    # 4. Kelompokkan data khusus jus ke dalam dictionary
    jus_totals = {
        "alpukat": totals.alpukat,
        "mangga": totals.mangga,
        "jeruk": totals.jeruk,
        "jambu": totals.jambu,
        "strobery": totals.strobery
    }

    # 5. Cari jus terlaris dan tersepi
    jus_terlaris = max(jus_totals, key=jus_totals.get)
    jus_tersepi = min(jus_totals, key=jus_totals.get)

    return {
        "kpi": {
            "total_penjualan_mie_ayam": int(totals.mie_ayam),
            "jus_terlaris": jus_terlaris,
            "jus_tersepi": jus_tersepi
        }
    }

@router.get("/omzet-trend")
def get_omzet_trend(db: Session = Depends(get_db)):
    # Ambil 7 data terbaru (desc), lalu limit 7
    sales_data = db.query(Sales.date, Sales.omzet).order_by(Sales.date.desc()).limit(7).all()
    
    # Balik urutan list-nya (reverse) agar di grafik tampil dari hari tertua -> terbaru
    sales_data.reverse()

    return {
        "labels": [data.date.strftime("%Y-%m-%d") for data in sales_data],
        "data": [data.omzet for data in sales_data]
    }

@router.get("/menu-composition")
def get_menu_composition(db: Session = Depends(get_db)):
    # 1. Buat subquery untuk membatasi 7 hari terakhir
    subq = db.query(Sales).order_by(Sales.date.desc()).limit(7).subquery()

    # 2. Jumlahkan porsi masing-masing menu dari 7 hari tersebut
    totals = db.query(
        func.sum(subq.c.mie_ayam).label('mie_ayam'),
        func.sum(subq.c.alpukat).label('alpukat'),
        func.sum(subq.c.mangga).label('mangga'),
        func.sum(subq.c.jeruk).label('jeruk'),
        func.sum(subq.c.jambu).label('jambu'),
        func.sum(subq.c.strobery).label('strobery')
    ).first()

    # 3. Handle jika data kosong
    if not totals or totals.mie_ayam is None:
        return {"labels": [], "data": []}

    # 4. Masukkan ke dalam dictionary
    menu_totals = {
        "Mie Ayam": int(totals.mie_ayam),
        "Alpukat": int(totals.alpukat),
        "Mangga": int(totals.mangga),
        "Jeruk": int(totals.jeruk),
        "Jambu": int(totals.jambu),
        "Strobery": int(totals.strobery)
    }

    # 5. Urutkan descending berdasarkan value (penjualan), lalu ambil 5 teratas
    top_5_menus = sorted(menu_totals.items(), key=lambda x: x[1], reverse=True)[:5]

    # 6. Format output menjadi array
    return {
        "labels": [item[0] for item in top_5_menus],
        "data": [item[1] for item in top_5_menus]
    }