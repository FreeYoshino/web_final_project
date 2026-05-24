from sqlalchemy.orm import Session

from app.models.user import User
from app.crud.user import UserCrud
from app.schemas.user import UserCreate, UserResponse
from app.services.password import PasswordService

class UserService:
    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> UserResponse:
        """
        商業邏輯: 驗證、正規化、建立使用者，並回傳 API response
        """

        normalized_email = user_in.email.strip().lower()
        existing_user = db.query(User).filter(User.email == normalized_email).first()
        if existing_user is not None:
            raise ValueError("信箱已被使用")

        user_data = user_in.model_dump(exclude={"password"})
        user_data["email"] = normalized_email
        user_data["password_hash"] = PasswordService.hash_password(user_in.password)

        user = UserCrud.create_user(db, user_data)
        return UserResponse.model_validate(user)
