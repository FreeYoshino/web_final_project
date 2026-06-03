import math
from uuid import UUID

from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.settlement import SettlementCrud
from app.models.expense import Expense, ExpenseSplit
from app.models.group import Group, GroupMember
from app.models.settlement import Settlement
from app.models.user import User
from app.schemas.settlement import (
    SettlementCreate,
    SettlementCreateWithPayer,
    SettlementListResponse,
    SettlementResponse,
)

class SettlementService:
    @staticmethod
    def create_settlement(db: Session, settlement_in: SettlementCreate, current_user_id: UUID) -> Settlement:
        """
        商業邏輯: 驗證與建立結算記錄
        """
        SettlementService._validate_settlement(db, settlement_in, current_user_id)
        settlement_in_with_payer = SettlementCreateWithPayer.model_validate(
            {
                **settlement_in.model_dump(),
                "payer_id": current_user_id,
            }
        )
        return SettlementCrud.create_settlement(db, settlement_in_with_payer)

    @staticmethod
    def get_group_settlement_list(
        db: Session,
        group_id: UUID,
        page: int,
        size: int,
        current_user_id: UUID,
    ) -> SettlementListResponse:
        """
        處理商業邏輯: 計算分頁並組裝結算交易回傳結構
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

        skip = (page - 1) * size
        total, settlements_db = SettlementCrud.get_group_settlements(
            db=db,
            group_id=group_id,
            skip=skip,
            limit=size,
        )

        pages = math.ceil(total / size) if total > 0 else 0
        settlements = []

        for settlement in settlements_db:
            settlement_response = SettlementResponse.model_validate(
                {
                    **settlement.__dict__,
                    "payer_name": settlement.payer.username,
                    "receiver_name": settlement.receiver.username,
                    "group_name": settlement.group.name,
                    "expense_description": (
                        settlement.expense.description if settlement.expense else None
                    ),
                }
            )
            settlements.append(settlement_response)

        return SettlementListResponse(
            settlements=settlements,
            total=total,
            page=page,
            size=size,
            pages=pages,
        )

    @staticmethod
    def _validate_settlement(db: Session, settlement_in: SettlementCreate, current_user_id: UUID) -> None:
        """建立結算前的商業驗證"""
        if current_user_id == settlement_in.receiver_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="付款人與收款人不能是同一人",
            )

        payer = db.scalar(select(User).where(User.id == current_user_id))
        if payer is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="付款人不存在"
            )

        receiver = db.scalar(select(User).where(User.id == settlement_in.receiver_id))
        if receiver is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="收款人不存在"
            )

        group = db.scalar(select(Group).where(Group.id == settlement_in.group_id))
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="群組不存在"
            )

        payer_in_group = db.scalar(
            select(GroupMember).where(
                GroupMember.group_id == settlement_in.group_id,
                GroupMember.user_id == current_user_id,
            )
        )
        if payer_in_group is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="付款人不是群組成員"
            )

        receiver_in_group = db.scalar(
            select(GroupMember).where(
                GroupMember.group_id == settlement_in.group_id,
                GroupMember.user_id == settlement_in.receiver_id,
            )
        )
        if receiver_in_group is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="收款人不是群組成員"
            )

        if settlement_in.expense_id is not None:
            expense = db.scalar(select(Expense).where(Expense.id == settlement_in.expense_id))
            if expense is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="相關費用不存在"
                )
            if expense.group_id != settlement_in.group_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="相關費用不屬於此群組"
                )

            payer_split = db.scalar(
                select(ExpenseSplit).where(
                    ExpenseSplit.expense_id == settlement_in.expense_id,
                    ExpenseSplit.user_id == current_user_id,
                    ExpenseSplit.is_settled.is_(False),
                )
            )
            if payer_split is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="付款人在該費用中沒有可結清的分攤明細",
                )

        else:
            pending_split = db.scalar(
                select(ExpenseSplit)
                .join(
                    Expense,
                    Expense.id == ExpenseSplit.expense_id,
                )
                .where(
                    Expense.group_id == settlement_in.group_id,
                    ExpenseSplit.user_id == current_user_id,
                    ExpenseSplit.is_settled.is_(False),
                )
            )
            if pending_split is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="付款人沒有可結清的分攤明細",
                )
