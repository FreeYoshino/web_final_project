# 測試連線
from fastapi import FastAPI
from .db.database import engine, Base

app = FastAPI(title="Roommate Sync API")

@app.get("/")
def read_root():
    return {"message": "Database environment is ready!"}