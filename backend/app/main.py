# 測試連線
from fastapi import FastAPI
from .db.database import engine, Base

# 啟動時自動建立所有在 models 裡定義的資料表 
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Roommate Sync API")

@app.get("/")
def read_root():
    return {"message": "Database environment is ready!"}