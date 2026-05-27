from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.group import Group, GroupMember
from app.schemas.group import GroupCreate


class GroupCrud:
    @staticmethod
    def create_group(db: Session, group_in: GroupCreate) -> Group:
        """建立群組與建立者的 admin 成員關係"""

        new_group = Group(**group_in.model_dump())

        try:
            db.add(new_group)
            db.flush()

            db.add(
                GroupMember(
                    group_id=new_group.id,
                    user_id=group_in.creator_id,
                    role="admin",
                )
            )
            db.commit()
            db.refresh(new_group)
            return new_group
        except SQLAlchemyError:
            db.rollback()
            raise