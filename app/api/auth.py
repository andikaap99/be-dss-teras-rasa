import bcrypt
import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserLogin

router = APIRouter()


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Dependency untuk koneksi database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # 1. Cari user berdasarkan username
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kredensial tidak valid")

    # 2. Verifikasi kecocokan password bcrypt
    is_password_correct = bcrypt.checkpw(
        user_data.password.encode('utf-8'), 
        db_user.password_hash.encode('utf-8')
    )
    
    if not is_password_correct:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kredensial tidak valid")

    # 3. Buat Token JWT (berlaku 24 jam)
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {"sub": db_user.username, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer", "message": "Login berhasil"}