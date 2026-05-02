import bcrypt
from app.database.database import SessionLocal
from app.models.user import User

db = SessionLocal()

username_input = "admin"
password_input = "dikaganteng123"

salt = bcrypt.gensalt()
hashed_pwd = bcrypt.hashpw(password_input.encode('utf-8'), salt)

new_user = User(username=username_input, password_hash=hashed_pwd.decode('utf-8'))

db.add(new_user)
db.commit()
db.close()

print(f"User '{username_input}' berhasil dibuat dengan password terenkripsi!")