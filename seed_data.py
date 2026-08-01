import random
from datetime import date, timedelta
import bcrypt
from app.database.database import SessionLocal
from app.models.user import User
from app.models.sales import Menu, Transaction

USERNAME = "admin"
PASSWORD = "password123"


def seed_user(db):
    existing = db.query(User).filter(User.username == USERNAME).first()
    if existing:
        print(f"  User '{USERNAME}' sudah ada, skip.")
        return

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(PASSWORD.encode("utf-8"), salt)
    user = User(username=USERNAME, password_hash=hashed.decode("utf-8"))
    db.add(user)
    db.commit()
    print(f"  User '{USERNAME}' berhasil dibuat.")


def seed_transactions(db):
    menus = db.query(Menu).all()
    menu_map = {m.name: m for m in menus}

    if not menu_map:
        print("  Tidak ada menu ditemukan, skip seed transaksi.")
        return

    today = date.today()
    start_date = today - timedelta(days=13)

    existing_dates = set(
        row[0] for row in db.query(Transaction.date).distinct().all()
    )

    RANGE_QTY = {
        "mie_ayam": (15, 40),
        "alpukat": (3, 12),
        "mangga": (4, 15),
        "jeruk": (3, 12),
        "jambu": (2, 10),
        "strobery": (3, 12),
    }

    tx_count = 0
    current = start_date
    while current <= today:
        if current in existing_dates:
            current += timedelta(days=1)
            continue

        for menu_name, menu in menu_map.items():
            min_q, max_q = RANGE_QTY.get(menu_name, (2, 8))
            qty = random.randint(min_q, max_q)
            total_price = qty * menu.price

            tx = Transaction(
                date=current,
                menu_id=menu.id,
                quantity=qty,
                total_price=total_price,
            )
            db.add(tx)
            tx_count += 1

        current += timedelta(days=1)

    db.commit()
    print(f"  {tx_count} transaksi harian di-seed (14 hari).")


def run_seed():
    print("=" * 40)
    print("SEED DATA AWAL")
    print("=" * 40)

    db = SessionLocal()
    try:
        print("\n[1/2] Seed user admin...")
        seed_user(db)

        print("\n[2/2] Seed transaksi harian...")
        seed_transactions(db)
    finally:
        db.close()

    print("\n" + "=" * 40)
    print("SEED SELESAI!")
    print("=" * 40)


if __name__ == "__main__":
    run_seed()
