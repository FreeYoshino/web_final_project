import math
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.group import Group, GroupMember
from app.models.user import User

from app.crud.expense import create_group_expense as create_group_expense_crud
from app.crud.expense import get_group_expenses
from app.schemas.expense import (
    ExpenseCreateWithPayer,
    ExpenseListResponse,
    ExpenseResponse,
)
from app.services.expense_split_helper import calculate_split_amounts


class ExpenseService:
    @staticmethod
    def create_group_expense(db: Session, expense_in, current_user_id: UUID):
        """建立群組費用前的商業邏輯驗證與資料正規化"""

        group = db.scalar(select(Group).where(Group.id == expense_in.group_id))
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="群組不存在"
            )

        payer = db.scalar(select(User).where(User.id == current_user_id))
        if payer is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="付款人不存在"
            )

        member_ids = set(
            db.scalars(
                select(GroupMember.user_id).where(
                    GroupMember.group_id == expense_in.group_id
                )
            ).all()
        )
        if not member_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="群組沒有任何成員"
            )

        if current_user_id not in member_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="付款人不是群組成員"
            )

        split_user_ids = [split.user_id for split in expense_in.splits]
        if len(split_user_ids) != len(set(split_user_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分攤明細中包含重複使用者",
            )

        if any(user_id not in member_ids for user_id in split_user_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分攤明細中包含非群組成員",
            )

        try:
            split_amounts = calculate_split_amounts(
                amount=expense_in.amount,
                split_type=expense_in.split_type,
                splits=expense_in.splits,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc

        expense_in_with_payer = ExpenseCreateWithPayer.model_validate(
            {
                **expense_in.model_dump(),
                "paid_by_id": current_user_id,
            }
        )
        return create_group_expense_crud(
            db=db,
            expense_in=expense_in_with_payer,
            split_amounts=split_amounts,
        )

    @staticmethod
    def get_group_expense_list(
        db: Session,
        group_id: UUID,
        page: int,
        size: int,
        current_user_id: UUID,
    ) -> ExpenseListResponse:
        """
        處理商業邏輯: 計算分頁、計算結算金額、並組裝回傳結構
        """

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

        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="page must be greater than 0",
            )
        if size < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="size must be greater than 0",
            )

        # 計算資料庫 offset
        skip = (page - 1) * size

        # 呼叫 CRUD 拿資料
        total, expenses_db = get_group_expenses(
            db=db, group_id=group_id, skip=skip, limit=size
        )

        # 計算總頁數
        pages = math.ceil(total / size) if total > 0 else 0
        items = []

        # 資料轉換與金額計算
        for expense in expenses_db:
            settled_amount = sum(
                (split.split_amount for split in expense.splits if split.is_settled),
                Decimal("0.00"),
            )
            pending_amount = sum(
                (
                    split.split_amount
                    for split in expense.splits
                    if not split.is_settled
                ),
                Decimal("0.00"),
            )

            splits = [
                {
                    "id": split.id,
                    "user_id": split.user_id,
                    "user_name": split.user.username,
                    "split_amount": split.split_amount,
                    "is_settled": split.is_settled,
                    "settled_at": split.settled_at,
                }
                for split in expense.splits
            ]

            expense_response = ExpenseResponse.model_validate(
                {
                    **expense.__dict__,
                    "payer_name": expense.payer.username,
                    "group_name": expense.group.name,
                    "splits": splits,
                    "settled_amount": settled_amount,
                    "pending_amount": pending_amount,
                }
            )
            items.append(expense_response)

        return ExpenseListResponse(
            items=items, total=total, page=page, size=size, pages=pages
        )
