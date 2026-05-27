from typing import Sequence, Tuple
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.expense import Expense, ExpenseSplit
from app.models.group import Group
from app.models.settlement import Settlement
from app.schemas.settlement import SettlementCreate

class SettlementCrud:
    @staticmethod
    def create_settlement(db: Session, settlement_in: SettlementCreate) -> Settlement:
        """建立一筆結算紀錄"""

        new_settlement = Settlement(**settlement_in.model_dump())
        try:
            db.add(new_settlement)
            db.flush()

            SettlementCrud._mark_related_splits_settled(db, settlement_in)

            db.commit()
            db.refresh(new_settlement)
            return new_settlement
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def _mark_related_splits_settled(db: Session, settlement_in: SettlementCreate) -> None:
        """將結算對應的 expense split 標記為已結清"""

        if settlement_in.expense_id is not None:
            splits = db.query(ExpenseSplit).filter(
                ExpenseSplit.expense_id == settlement_in.expense_id,
                ExpenseSplit.user_id == settlement_in.payer_id,
                ExpenseSplit.is_settled.is_(False),
            ).all()
        else:
            splits = db.query(ExpenseSplit).join(
                Expense,
                Expense.id == ExpenseSplit.expense_id,
            ).filter(
                Expense.group_id == settlement_in.group_id,
                ExpenseSplit.user_id == settlement_in.payer_id,
                ExpenseSplit.is_settled.is_(False),
            ).all()

        for split in splits:
            split.is_settled = True
            split.settled_at = settlement_in.transaction_date

    @staticmethod
    def get_group_settlements(
        db: Session,
        group_id: UUID,
        skip: int,
        limit: int,
    ) -> Tuple[int, Sequence[Settlement]]:
        """取得群組的結算交易列表 (含分頁與關聯資料)"""

        group = db.query(Group).filter(Group.id == group_id).first()
        if group is None:
            raise ValueError("群組不存在")

        total_statements = select(func.count(Settlement.id)).where(
            Settlement.group_id == group_id,
        )
        total = db.scalar(total_statements) or 0

        statements = (
            select(Settlement)
            .where(Settlement.group_id == group_id)
            .options(
                selectinload(Settlement.payer),
                selectinload(Settlement.receiver),
                selectinload(Settlement.group),
                selectinload(Settlement.expense),
            )
            .order_by(Settlement.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = db.execute(statements)
        settlements = result.scalars().all()

        return total, settlements