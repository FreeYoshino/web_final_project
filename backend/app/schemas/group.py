from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.base import BaseSchema, IDSchema, TimestampSchema
from app.schemas.user import UserResponse

GroupMemberRole = Literal["admin", "member"]


class GroupBase(BaseSchema):
    """Group 的基礎欄位定義"""

    creator_id: UUID = Field(..., description="群組建立者 ID")
    name: str = Field(..., min_length=1, max_length=100, description="群組名稱")
    description: Optional[str] = Field(None, max_length=255, description="群組描述")
    avatar_url: Optional[str] = Field(None, max_length=500, description="群組頭像網址")

    @field_validator("name", mode="before")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        value = value.strip()
        if not value:
            raise ValueError("欄位不可為空白")
        return value

    @field_validator("description", "avatar_url", mode="before")
    @classmethod
    def strip_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        value = value.strip()
        return value or None


class GroupCreate(GroupBase):
    """建立 Group 時的輸入 schema"""
    pass

class GroupResponse(GroupBase, IDSchema, TimestampSchema):
    """Group 的回應 schema"""
    pass

class GroupMemberBase(BaseSchema):
    """GroupMember 的共用欄位"""

    role: GroupMemberRole = Field(default="member", description="群組成員角色")

class GroupMembersCreate(GroupMemberBase):
    """批次加入多位成員到群組的輸入 schema"""

    user_ids: List[UUID] = Field(..., min_length=1, description="要加入群組的使用者 ID 清單")

class GroupMemberResponse(GroupMemberBase, IDSchema):
    """GroupMember 的回應 schema"""

    group_id: UUID = Field(..., description="群組 ID")
    user_id: UUID = Field(..., description="使用者 ID")
    joined_at: datetime = Field(..., description="加入時間")

class GroupMemberListResponse(BaseSchema):
    """群組成員清單回應 schema"""

    group_id: UUID = Field(..., description="群組 ID")
    members: List[GroupMemberResponse] = Field(default_factory=list, description="成員清單")
