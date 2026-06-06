from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID

from app.models.user import User
from app.models.group import Group
from app.crud.user import UserCrud
from app.schemas.user import UserCreate, UserResponse, UserSearchResponse, UserSearchResult
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

    @staticmethod
    def search_users(
        db: Session,
        query: str,
        limit: int = 20,
        exclude_group_id: UUID | None = None,
        current_user_id: UUID | None = None,
    ) -> UserSearchResponse:
        """
        搜尋使用者的商業邏輯

        Args:
            query: 搜尋關鍵字（至少 1 個字元）
            limit: 回傳筆數上限（1~50）
            exclude_group_id: 排除已在此群組中的使用者
            current_user_id: 當前登入者 ID（用於自我排除）

        Returns:
            UserSearchResponse: 符合條件的使用者清單與總數

        Raises:
            HTTPException: 搜尋字串為空、群組不存在
        """

        # 正規化搜尋字串
        normalized_query = query.strip()
        if not normalized_query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="搜尋關鍵字不可為空白",
            )

        # 限制回傳筆數範圍
        limit = max(1, min(limit, 50))

        # 若指定排除群組，先確認群組存在
        if exclude_group_id is not None:
            group = db.scalar(select(Group).where(Group.id == exclude_group_id))
            if group is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="指定的群組不存在",
                )

        users, total = UserCrud.search_users(
            db=db,
            query=normalized_query,
            limit=limit,
            exclude_group_id=exclude_group_id,
            exclude_user_id=current_user_id,
        )

        user_list = [
            UserSearchResult(
                id=user.id,
                username=user.username,
                name=user.name,
            )
            for user in users
        ]

        return UserSearchResponse(users=user_list, total=total)
