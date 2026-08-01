import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

MYSQL_URL = os.getenv("MYSQL_URL", "")
if MYSQL_URL:
    if MYSQL_URL.startswith("mysql://"):
        SQLALCHEMY_DATABASE_URL = "mysql+pymysql://" + MYSQL_URL[len("mysql://"):]
    else:
        SQLALCHEMY_DATABASE_URL = MYSQL_URL
else:
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost/dss_mie_ayam"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
