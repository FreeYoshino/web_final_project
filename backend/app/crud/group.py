from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload
from uuid import UUID

from app.models.group import Group, GroupMember
from app.schemas.group import GroupCreate


class GroupCrud:
    @staticmethod
    def create_group(db: Session, group_in: GroupCreate, creator_id: UUID) -> Group:
        """建立群組與建立者的 admin 成員關係"""

        new_group = Group(**group_in.model_dump(), creator_id=creator_id)

        try:
            db.add(new_group)
            db.flush()

            db.add(
                GroupMember(
                    group_id=new_group.id,
                    user_id=creator_id,
                    role="admin",
                )
            )
            db.commit()
            db.refresh(new_group)
            return new_group
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def add_members_to_group(
        db: Session,
        group_id: UUID,
        user_ids: list[UUID],
        role: str = "member",
    ) -> list[GroupMember]:
        """批次加入群組成員"""

        new_members = [
            GroupMember(group_id=group_id, user_id=user_id, role=role)
            for user_id in user_ids
        ]

        try:
            db.add_all(new_members)
            db.commit()

            for member in new_members:
                db.refresh(member)

            return new_members
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def get_group_members(db: Session, group_id: UUID) -> list[GroupMember]:
        """取得群組成員列表（含使用者資訊）"""
        return list(
            db.scalars(
                select(GroupMember)
                .where(GroupMember.group_id == group_id)
                .options(selectinload(GroupMember.user))
            ).all()
        )

    @staticmethod
    def get_user_groups(db: Session, user_id: UUID) -> list[GroupMember]:
        """取得使用者所屬的所有群組成員記錄（含群組資訊）"""
        return list(
            db.scalars(
                select(GroupMember)
                .where(GroupMember.user_id == user_id)
                .options(selectinload(GroupMember.group))
            ).all()
        )

    @staticmethod
    def get_group_member_counts(
        db: Session, group_ids: list[UUID]
    ) -> dict[UUID, int]:
        """批次查詢多個群組的成員數量"""
        if not group_ids:
            return {}
        rows = (
            db.execute(
                select(
                    GroupMember.group_id,
                    func.count(GroupMember.id).label("member_count"),
                )
                .where(GroupMember.group_id.in_(group_ids))
                .group_by(GroupMember.group_id)
            )
        ).all()
        return {row.group_id: row.member_count for row in rows}