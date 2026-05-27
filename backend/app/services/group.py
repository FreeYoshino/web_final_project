from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.group import GroupCrud
from app.models.group import Group
from app.models.user import User
from app.schemas.group import GroupCreate, GroupResponse

class GroupService:
    @staticmethod
    def create_group(db: Session, group_in: GroupCreate) -> GroupResponse:
        """建立群組前的商業邏輯驗證與資料正規化"""

        creator = db.scalar(select(User).where(User.id == group_in.creator_id))
        if creator is None:
            raise ValueError("建立者不存在")

        existing_group = db.scalar(
            select(Group).where(
                Group.creator_id == group_in.creator_id,
                Group.name == group_in.name,
            )
        )
        if existing_group is not None:
            raise ValueError("同一建立者已存在相同名稱的群組")

        group = GroupCrud.create_group(db, group_in)
        return GroupResponse.model_validate(group)