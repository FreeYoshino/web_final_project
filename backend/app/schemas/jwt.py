from typing import Literal

from pydantic import EmailStr, Field, field_validator

from app.schemas.base import BaseSchema


class LoginRequest(BaseSchema):
	"""前端登入時提供的資料 schema"""

	email: EmailStr = Field(..., description="使用者電子郵件")
	password: str = Field(..., min_length=1, max_length=128, description="使用者密碼")

	@field_validator("email", mode="before")
	@classmethod
	def strip_email(cls, value: str) -> str:
		if not isinstance(value, str):
			return value
		value = value.strip()
		if not value:
			raise ValueError("欄位不可為空白")
		return value


class Token(BaseSchema):
	"""登入成功後回傳的 JWT access token schema"""

	access_token: str = Field(..., description="JWT access token")
	token_type: Literal["bearer"] = Field(default="bearer", description="token 類型")
