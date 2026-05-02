from sqlalchemy import Column, Integer, Date
from app.database.database import Base

class Sales(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True, nullable=False) # unique=True penting untuk fitur replace
    mie_ayam = Column(Integer, default=0)
    alpukat = Column(Integer, default=0)
    mangga = Column(Integer, default=0)
    jeruk = Column(Integer, default=0)
    jambu = Column(Integer, default=0)
    strobery = Column(Integer, default=0)