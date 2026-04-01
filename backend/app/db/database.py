# ORM 連線設定
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 讀取 .env 檔案
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 建立連線引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 建立 Session 類別 用來操作資料庫
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 所有的 Model 都要繼承這個 Base
Base = declarative_base()

# 依賴注入: 獲取資料庫 Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()