from fastapi import FastAPI

from app.database.db import engine
from app.database.base import Base

from app.models.user import User

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "FixMyResume Backend Running"}

@app.get("/test-db")
def test_db():
    return {"message": "Database connected successfully"}