import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database.database import engine, SessionLocal
from app.models.user import User
from app.models.sales import Menu, Ingredient, MenuIngredient, Transaction

DB_URL = "mysql+pymysql://root:@localhost/dss_mie_ayam"

MENU_MASTER = [
    {"name": "mie_ayam", "price": 15000},
    {"name": "alpukat", "price": 12000},
    {"name": "mangga", "price": 12000},
    {"name": "jeruk", "price": 10000},
    {"name": "jambu", "price": 10000},
    {"name": "strobery", "price": 12000},
]

BAHAN_BAKU_MASTER = [
    {"name": "Mie basah", "unit": "gram"},
    {"name": "Daging ayam (cincang/dadu)", "unit": "gram"},
    {"name": "Minyak ayam/bawang", "unit": "ml"},
    {"name": "Kecap asin", "unit": "ml"},
    {"name": "Kecap manis", "unit": "ml"},
    {"name": "Saus tiram", "unit": "gram"},
    {"name": "Garam", "unit": "gram"},
    {"name": "Kaldu bubuk", "unit": "gram"},
    {"name": "Merica bubuk", "unit": "gram"},
    {"name": "Bawang putih (halus)", "unit": "gram"},
    {"name": "Bawang merah (halus)", "unit": "gram"},
    {"name": "Air/Kuah kaldu", "unit": "ml"},
    {"name": "Daging Alpukat", "unit": "gram"},
    {"name": "Gula Pasir", "unit": "gram"},
    {"name": "Susu Kental Manis", "unit": "ml"},
    {"name": "Air Matang / Es Batu", "unit": "ml"},
    {"name": "Daging Mangga", "unit": "gram"},
    {"name": "Susu Kental Manis / UHT", "unit": "ml"},
    {"name": "Air Perasan Jeruk", "unit": "ml"},
    {"name": "Daging Jambu Biji Merah", "unit": "gram"},
    {"name": "Buah Stroberi Segar", "unit": "gram"},
]

MENU_INGREDIENTS = {
    "mie_ayam": [
        {"name": "Mie basah", "quantity": 100},
        {"name": "Daging ayam (cincang/dadu)", "quantity": 85},
        {"name": "Minyak ayam/bawang", "quantity": 15},
        {"name": "Kecap asin", "quantity": 5},
        {"name": "Kecap manis", "quantity": 18},
        {"name": "Saus tiram", "quantity": 5},
        {"name": "Garam", "quantity": 2.5},
        {"name": "Kaldu bubuk", "quantity": 2.5},
        {"name": "Merica bubuk", "quantity": 1},
        {"name": "Bawang putih (halus)", "quantity": 6.5},
        {"name": "Bawang merah (halus)", "quantity": 9},
        {"name": "Air/Kuah kaldu", "quantity": 175},
    ],
    "alpukat": [
        {"name": "Daging Alpukat", "quantity": 110},
        {"name": "Gula Pasir", "quantity": 17.5},
        {"name": "Susu Kental Manis", "quantity": 30},
        {"name": "Air Matang / Es Batu", "quantity": 125},
    ],
    "mangga": [
        {"name": "Daging Mangga", "quantity": 110},
        {"name": "Gula Pasir", "quantity": 15},
        {"name": "Susu Kental Manis / UHT", "quantity": 15},
        {"name": "Air Matang / Es Batu", "quantity": 150},
    ],
    "jeruk": [
        {"name": "Air Perasan Jeruk", "quantity": 110},
        {"name": "Gula Pasir", "quantity": 22.5},
        {"name": "Air Matang / Es Batu", "quantity": 100},
    ],
    "jambu": [
        {"name": "Daging Jambu Biji Merah", "quantity": 110},
        {"name": "Gula Pasir", "quantity": 20},
        {"name": "Susu Kental Manis / UHT", "quantity": 15},
        {"name": "Air Matang / Es Batu", "quantity": 175},
    ],
    "strobery": [
        {"name": "Buah Stroberi Segar", "quantity": 90},
        {"name": "Gula Pasir", "quantity": 22.5},
        {"name": "Susu Kental Manis / UHT", "quantity": 20},
        {"name": "Air Matang / Es Batu", "quantity": 125},
    ],
}


def run_migration():
    print("=" * 50)
    print("MEMULAI MIGRASI DATABASE")
    print("=" * 50)

    conn = pymysql.connect(host="localhost", user="root", password="", database="dss_mie_ayam")
    cursor = conn.cursor()

    print("\n[1/7] Cek tabel lama...")
    cursor.execute("SHOW TABLES")
    old_tables = [row[0] for row in cursor.fetchall()]
    print(f"  Tabel ditemukan: {old_tables}")

    print("\n[2/7] Backup data sales lama...")
    old_data = []
    if "sales" in old_tables:
        cursor.execute("SELECT * FROM sales")
        old_data = cursor.fetchall()
        cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='dss_mie_ayam' AND TABLE_NAME='sales' ORDER BY ORDINAL_POSITION")
        old_columns = [row[0] for row in cursor.fetchall()]
        print(f"  Backup {len(old_data)} baris data dari tabel 'sales'")
    else:
        print("  Tabel 'sales' tidak ditemukan, skip backup")

    print("\n[3/7] Drop tabel lama...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for tbl in ["sales", "menu_ingredients", "ingredients", "menus", "transactions", "users"]:
        cursor.execute(f"DROP TABLE IF EXISTS {tbl}")
        print(f"  Drop tabel '{tbl}' (jika ada)")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    print("\n[4/7] Buat tabel baru...")
    cursor.execute("""
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL
        )
    """)
    print("  Tabel 'users' dibuat")

    cursor.execute("""
        CREATE TABLE menus (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            price INT NOT NULL DEFAULT 0
        )
    """)
    print("  Tabel 'menus' dibuat")

    cursor.execute("""
        CREATE TABLE ingredients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            unit VARCHAR(20) NOT NULL
        )
    """)
    print("  Tabel 'ingredients' dibuat")

    cursor.execute("""
        CREATE TABLE menu_ingredients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            menu_id INT NOT NULL,
            ingredient_id INT NOT NULL,
            quantity FLOAT NOT NULL,
            FOREIGN KEY (menu_id) REFERENCES menus(id),
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
            UNIQUE KEY uk_menu_ingredient (menu_id, ingredient_id)
        )
    """)
    print("  Tabel 'menu_ingredients' dibuat")

    cursor.execute("""
        CREATE TABLE transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            menu_id INT NOT NULL,
            quantity INT NOT NULL DEFAULT 0,
            total_price INT NOT NULL DEFAULT 0,
            FOREIGN KEY (menu_id) REFERENCES menus(id),
            UNIQUE KEY uk_date_menu (date, menu_id)
        )
    """)
    print("  Tabel 'transactions' dibuat")

    print("\n[5/7] Seed data master...")
    for menu in MENU_MASTER:
        cursor.execute("INSERT INTO menus (name, price) VALUES (%s, %s)", (menu["name"], menu["price"]))
    print(f"  {len(MENU_MASTER)} menu di-insert")

    ingredient_id_map = {}
    for bahan in BAHAN_BAKU_MASTER:
        cursor.execute("INSERT INTO ingredients (name, unit) VALUES (%s, %s)", (bahan["name"], bahan["unit"]))
        ingredient_id_map[bahan["name"]] = cursor.lastrowid
    print(f"  {len(BAHAN_BAKU_MASTER)} bahan baku di-insert")

    menu_id_map = {}
    cursor.execute("SELECT id, name FROM menus")
    for row in cursor.fetchall():
        menu_id_map[row[1]] = row[0]

    mi_count = 0
    for menu_name, ingredients in MENU_INGREDIENTS.items():
        menu_id = menu_id_map[menu_name]
        for ing in ingredients:
            ing_id = ingredient_id_map[ing["name"]]
            cursor.execute(
                "INSERT INTO menu_ingredients (menu_id, ingredient_id, quantity) VALUES (%s, %s, %s)",
                (menu_id, ing_id, ing["quantity"])
            )
            mi_count += 1
    print(f"  {mi_count} relasi menu_ingredients di-insert")

    print("\n[6/7] Migrate data penjualan lama ke transactions...")
    if old_data:
        col_map = {col: idx for idx, col in enumerate(old_columns)}
        tx_count = 0
        for row in old_data:
            row_date = row[col_map["date"]]
            for menu_name in ["mie_ayam", "alpukat", "mangga", "jeruk", "jambu", "strobery"]:
                qty = row[col_map[menu_name]]
                if qty and qty > 0:
                    cursor.execute("SELECT price FROM menus WHERE name=%s", (menu_name,))
                    price_row = cursor.fetchone()
                    price = price_row[0] if price_row else 0
                    total = qty * price
                    try:
                        cursor.execute(
                            "INSERT INTO transactions (date, menu_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
                            (row_date, menu_id_map[menu_name], qty, total)
                        )
                        tx_count += 1
                    except pymysql.err.IntegrityError:
                        pass
        print(f"  {tx_count} transaksi di-migrate")
    else:
        print("  Tidak ada data lama untuk di-migrate")

    print("\n[7/7] Re-create user admin...")
    import bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw("dikaganteng123".encode("utf-8"), salt)
    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
        ("admin", hashed.decode("utf-8"))
    )
    print("  User 'admin' di-insert")

    conn.commit()
    cursor.close()
    conn.close()

    print("\n" + "=" * 50)
    print("MIGRASI SELESAI!")
    print("=" * 50)


if __name__ == "__main__":
    run_migration()
