from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import SessionLocal
from app.models.sales import Transaction, Menu
from app.core.deps import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_recent_dates(db, limit=7):
    rows = (
        db.query(Transaction.date)
        .distinct()
        .order_by(Transaction.date.desc())
        .limit(limit)
        .all()
    )
    return [row[0] for row in rows]


@router.get("/kpi")
def get_kpi(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    recent_dates = get_recent_dates(db, 7)
    if not recent_dates:
        return {"kpi": {"total_penjualan_mie_ayam": 0, "jus_terlaris": "-", "jus_tersepi": "-"}}

    min_date = min(recent_dates)

    mie_ayam_menu = db.query(Menu).filter(Menu.name == "mie_ayam").first()
    if not mie_ayam_menu:
        return {"kpi": {"total_penjualan_mie_ayam": 0, "jus_terlaris": "-", "jus_tersepi": "-"}}

    mie_ayam_total = (
        db.query(func.sum(Transaction.quantity))
        .filter(
            Transaction.date >= min_date,
            Transaction.menu_id == mie_ayam_menu.id,
        )
        .scalar()
        or 0
    )

    juice_menus = db.query(Menu).filter(Menu.name != "mie_ayam").all()
    juice_totals = {}
    for jm in juice_menus:
        total = (
            db.query(func.sum(Transaction.quantity))
            .filter(
                Transaction.date >= min_date,
                Transaction.menu_id == jm.id,
            )
            .scalar()
            or 0
        )
        juice_totals[jm.name] = total

    if not juice_totals:
        return {"kpi": {"total_penjualan_mie_ayam": int(mie_ayam_total), "jus_terlaris": "-", "jus_tersepi": "-"}}

    jus_terlaris = max(juice_totals, key=juice_totals.get)
    jus_tersepi = min(juice_totals, key=juice_totals.get)

    return {
        "kpi": {
            "total_penjualan_mie_ayam": int(mie_ayam_total),
            "jus_terlaris": jus_terlaris,
            "jus_tersepi": jus_tersepi,
        }
    }


@router.get("/omzet-trend")
def get_omzet_trend(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    results = (
        db.query(
            Transaction.date,
            func.sum(Transaction.total_price).label("daily_omzet"),
        )
        .group_by(Transaction.date)
        .order_by(Transaction.date.desc())
        .limit(7)
        .all()
    )

    results_list = list(results)
    results_list.reverse()

    return {
        "labels": [row.date.strftime("%Y-%m-%d") for row in results_list],
        "data": [int(row.daily_omzet) for row in results_list],
    }


@router.get("/menu-composition")
def get_menu_composition(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    recent_dates = get_recent_dates(db, 7)
    if not recent_dates:
        return {"labels": [], "data": []}

    min_date = min(recent_dates)

    results = (
        db.query(
            Menu.name,
            func.sum(Transaction.quantity).label("total_qty"),
        )
        .join(Transaction, Transaction.menu_id == Menu.id)
        .filter(Transaction.date >= min_date)
        .group_by(Menu.name)
        .order_by(func.sum(Transaction.quantity).desc())
        .limit(5)
        .all()
    )

    return {
        "labels": [row.name for row in results],
        "data": [int(row.total_qty) for row in results],
    }
