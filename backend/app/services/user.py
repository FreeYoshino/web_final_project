from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.crud.user import UserCrud
from app.schemas.user import UserCreate, UserResponse
from app.schemas.jwt import Token
from app.core.security import create_access_token
from app.services.password import PasswordService

class UserService:
    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> UserResponse:
        """
        商業邏輯: 驗證、正規化、建立使用者，並回傳 API response
        """

        normalized_email = user_in.email.strip().lower()
        existing_user = db.scalar(select(User).where(User.email == normalized_email))
        if existing_user is not None:
            raise ValueError("信箱已被使用")

        user_data = user_in.model_dump(exclude={"password"})
        user_data["email"] = normalized_email
        user_data["password_hash"] = PasswordService.hash_password(user_in.password)

        user = UserCrud.create_user(db, user_data)
        return UserResponse.model_validate(user)
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Token:
        """
        商業邏輯: 驗證使用者登入資訊，成功回傳 Token model 失敗拋出異常
        
        Raises:
            HTTPException: 用戶不存在或密碼錯誤
        """
        normalized_email = email.strip().lower()
        user = db.scalar(select(User).where(User.email == normalized_email))

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用戶不存在或信箱錯誤"
            )

        if not PasswordService.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="密碼錯誤"
            )

        access_token = create_access_token(data={"sub": str(user.id)})
        return Token(access_token=access_token)
