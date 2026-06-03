# ORM 連線設定
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from app.core.config import get_settings

settings = get_settings()
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 建立連線引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# 建立 Session 類別 用來操作資料庫
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)

# 所有的 Model 都要繼承這個 Base
class Base(DeclarativeBase):
    pass

# 依賴注入: 獲取資料庫 Session
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()