from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID

from app.crud.group import GroupCrud
from app.models.group import Group, GroupMember
from app.models.user import User
from app.schemas.group import (
    GroupCreate,
    GroupResponse,
    GroupMembersCreate,
    GroupMemberListResponse,
    GroupMemberResponse,
    UserGroupResponse,
    UserGroupListResponse,
)


class GroupService:
    @staticmethod
    def create_group(
        db: Session, group_in: GroupCreate, creator_id: UUID
    ) -> GroupResponse:
        """建立群組前的商業邏輯驗證與資料正規化"""

        creator = db.scalar(select(User).where(User.id == creator_id))
        if creator is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="建立者不存在"
            )

        existing_group = db.scalar(
            select(Group).where(
                Group.creator_id == creator_id,
                Group.name == group_in.name,
            )
        )
        if existing_group is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="同一建立者已存在相同名稱的群組",
            )

        group = GroupCrud.create_group(db, group_in, creator_id)
        return GroupResponse.model_validate(group)

    @staticmethod
    def add_members_to_group(
        db: Session,
        group_id: UUID,
        members_in: GroupMembersCreate,
        current_user_id: UUID,
    ) -> GroupMemberListResponse:
        """加入成員到群組的商業邏輯驗證與資料處理"""

        user_ids = members_in.user_ids

        if not user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="user_ids 不能為空"
            )

        if len(user_ids) != len(set(user_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="user_ids 不能重複"
            )

        group = db.scalar(select(Group).where(Group.id == group_id))
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="群組不存在"
            )

        current_user_in_group = db.scalar(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == current_user_id,
            )
        )
        if current_user_in_group is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="使用者不是群組成員"
            )

        users = db.scalars(select(User).where(User.id.in_(user_ids))).all()
        if len(users) != len(user_ids):
            existing_user_ids = {user.id for user in users}
            missing_user_ids = [
                str(user_id) for user_id in user_ids if user_id not in existing_user_ids
            ]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"以下使用者不存在: {', '.join(missing_user_ids)}",
            )

        existing_members = db.scalars(
            select(GroupMember.user_id).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id.in_(user_ids),
            )
        ).all()
        if existing_members:
            existing_member_ids = ", ".join(
                str(user_id) for user_id in existing_members
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"以下使用者已在群組中: {existing_member_ids}",
            )

        members = GroupCrud.add_members_to_group(
            db, group_id, user_ids, members_in.role
        )
        member_responses = [
            GroupMemberResponse.model_validate(
                {
                    **member.__dict__,
                    "username": member.user.username,
                    "name": member.user.name,
                }
            )
            for member in members
        ]

        return GroupMemberListResponse(group_id=group_id, members=member_responses)

    @staticmethod
    def get_group_members(
        db: Session, group_id: UUID, current_user_id: UUID
    ) -> GroupMemberListResponse:
        """取得群組成員清單的商業邏輯處理"""

        group = db.scalar(select(Group).where(Group.id == group_id))
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="群組不存在"
            )

        current_user_in_group = db.scalar(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == current_user_id,
            )
        )
        if current_user_in_group is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="使用者不是群組成員"
            )

        members = GroupCrud.get_group_members(db, group_id)
        member_responses = [
            GroupMemberResponse.model_validate(
                {
                    **member.__dict__,
                    "username": member.user.username,
                    "name": member.user.name,
                }
            )
            for member in members
        ]

        return GroupMemberListResponse(group_id=group_id, members=member_responses)

    @staticmethod
    def get_my_groups(
        db: Session, current_user_id: UUID
    ) -> UserGroupListResponse:
        """查詢當前使用者所在的所有群組"""

        memberships = GroupCrud.get_user_groups(db, current_user_id)

        if not memberships:
            return UserGroupListResponse(groups=[], total=0)

        group_ids = [m.group_id for m in memberships]
        member_counts = GroupCrud.get_group_member_counts(db, group_ids)

        groups = [
            UserGroupResponse(
                id=m.group.id,
                name=m.group.name,
                description=m.group.description,
                avatar_url=m.group.avatar_url,
                role=m.role,
                member_count=member_counts.get(m.group_id, 0),
                creator_id=m.group.creator_id,
                created_at=m.group.created_at,
                updated_at=m.group.updated_at,
            )
            for m in memberships
        ]

        return UserGroupListResponse(groups=groups, total=len(groups))
