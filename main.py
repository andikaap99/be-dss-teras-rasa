from fastapi import FastAPI
from app.database.database import engine
from app.models import user
from app.api import auth
from app.models import sales
from app.api import upload


user.Base.metadata.create_all(bind=engine)
sales.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(upload.router, prefix="/api", tags=["Data Sales"])

@app.get("/")
def read_root():
    return {"message": "Website Online!"}