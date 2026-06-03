from typing import Literal

from pydantic import EmailStr, Field, field_validator

from app.schemas.base import BaseSchema

class Token(BaseSchema):
	"""登入成功後回傳的 JWT access token schema"""

	access_token: str = Field(..., description="JWT access token")
	token_type: Literal["bearer"] = Field(default="bearer", description="token 類型")
