from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate, UserInDB, UserResponse

from app.services.password import PasswordService

class UserCrud:
    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        """建立一筆使用者資料"""

        # 驗證輸入資料的合理性
        user_in.email = user_in.email.strip().lower()  # 標準化 email 格式
        existing_user = db.query(User).filter(User.email == user_in.email).first()
        if existing_user is not None:
            raise ValueError("信箱已被使用")
        
        # 對密碼進行雜湊處理並轉成資料庫欄位名稱
        user_data = user_in.model_dump(exclude={"password"})
        user_data["password_hash"] = PasswordService.hash_password(user_in.password)
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