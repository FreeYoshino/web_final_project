from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from app.models.user import User
from app.models.group import GroupMember
from typing import Any

class UserCrud:
    @staticmethod
    def create_user(db: Session, user_data: dict[str, Any]) -> User:
        """建立一筆使用者資料"""
        new_user = User(**user_data)

        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
        except IntegrityError:
            # 捕捉並發情況下，Database Unique Constraint 觸發的錯誤
            db.rollback()
            raise ValueError("信箱已被使用")

        except Exception as e:
            # 捕捉其他非預期的資料庫錯誤
            db.rollback()
            raise e

    @staticmethod
    def search_users(
        db: Session,
        query: str,
        limit: int = 20,
        exclude_group_id: UUID | None = None,
        exclude_user_id: UUID | None = None,
    ) -> tuple[list[User], int]:
        """
        模糊搜尋使用者（by username / name）

        Args:
            query: 搜尋關鍵字（部分匹配，不區分大小寫）
            limit: 回傳筆數上限
            exclude_group_id: 排除已在此群組中的使用者
            exclude_user_id: 排除特定使用者（例如搜尋者本人）

        Returns:
            (符合條件的使用者清單, 總筆數)
        """
        pattern = f"%{query}%"

        # 基礎條件：username 或 name 模糊匹配
        base_filters = (
            (User.username.ilike(pattern)) | (User.name.ilike(pattern))
        )

        # 排除特定使用者（自我排除）
        if exclude_user_id is not None:
            base_filters = base_filters & (User.id != exclude_user_id)

        # 排除已在指定群組中的使用者
        if exclude_group_id is not None:
            subquery = (
                select(GroupMember.user_id)
                .where(GroupMember.group_id == exclude_group_id)
            )
            base_filters = base_filters & (User.id.not_in(subquery))

        # 查詢總筆數
        count_stmt = select(func.count()).select_from(User).where(base_filters)
        total = db.scalar(count_stmt) or 0

        # 查詢使用者清單
        stmt = (
            select(User)
            .where(base_filters)
            .order_by(User.username)
            .limit(limit)
        )
        users = list(db.scalars(stmt).all())

        return users, total