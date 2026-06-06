from pydantic import Field, EmailStr, field_validator
from typing import Optional, List
from uuid import UUID
from app.schemas.base import BaseSchema, TimestampSchema, IDSchema

"""User基礎schema"""


class UserBase(BaseSchema):
    """User的基礎欄位定義"""

    username: str = Field(..., min_length=1, max_length=50, description="使用者名稱")
    email: EmailStr = Field(..., description="使用者電子郵件")
    phone: Optional[str] = Field(None, max_length=20, description="使用者電話")
    name: str = Field(..., min_length=1, max_length=100, description="用戶真實名稱")

    @field_validator("username", "name", mode="before")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        value = value.strip()
        if not value:
            raise ValueError("欄位不可為空白")
        return value

    @field_validator("phone", mode="before")
    @classmethod
    def strip_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        value = value.strip()
        return value or None


class UserCreate(UserBase):
    """建立User 時的輸入schema"""

    password: str = Field(..., min_length=8, max_length=128, description="使用者密碼")


class UserInDB(UserBase):
    """User 內部儲存用schema"""

    password_hash: str = Field(..., max_length=255, description="使用者密碼雜湊")


"""User的回應schema"""


class UserResponse(UserBase, TimestampSchema, IDSchema):
    """User的回應schema"""

    pass


"""使用者搜尋 schema"""


class UserSearchResult(BaseSchema):
    """搜尋結果中單一使用者的精簡表示（不暴露 email、phone 等敏感欄位）"""

    id: UUID = Field(..., description="使用者 ID")
    username: str = Field(..., description="使用者帳號名稱")
    name: str = Field(..., description="使用者真實姓名")


class UserSearchResponse(BaseSchema):
    """使用者搜尋回應"""

    users: List[UserSearchResult] = Field(
        default_factory=list, description="符合條件的使用者清單"
    )
    total: int = Field(..., ge=0, description="符合條件的使用者總數")
