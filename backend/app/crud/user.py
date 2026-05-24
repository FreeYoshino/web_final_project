from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from typing import Any

class UserCrud:
    @staticmethod
    def create_user(db: Session, user_data: dict[str, Any]) -> User:
        """建立一筆使用者資料"""
        new_user = User(**user_data)

        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
        except IntegrityError:
            # 捕捉並發情況下，Database Unique Constraint 觸發的錯誤
            db.rollback()
            raise ValueError("信箱已被使用")

        except Exception as e:
            # 捕捉其他非預期的資料庫錯誤
            db.rollback()
            raise e  