from decimal import Decimal
from typing import Sequence, Tuple
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.crud.balance import get_group_balances as crud_get_group_balances
from app.models.expense import Expense, ExpenseSplit
from app.models.group import Group
from app.models.settlement import Settlement
from app.schemas.settlement import SettlementCreateWithPayer

class SettlementCrud:
    @staticmethod
    def create_settlement(db: Session, settlement_in: SettlementCreateWithPayer) -> Settlement:
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
    def _mark_related_splits_settled(db: Session, settlement_in: SettlementCreateWithPayer) -> None:
        """將結算對應的 expense split 標記為已結清

        - expense-specific settlement（有 expense_id）：直接標記該費用的對應 split
        - 批次結算（無 expense_id）：檢查群組內「所有成員」的 net_balance，
          對任何 net_balance >= 0 的成員，將其所有未結清 split 標記為已結清。
          因為 net_balance >= 0 代表該成員已無待償還債務（債務已透過
          settlement 或與他人債務互相沖抵），即使個別 split 未曾被明確結算。
        """

        if settlement_in.expense_id is not None:
            splits = db.scalars(
                select(ExpenseSplit).where(
                    ExpenseSplit.expense_id == settlement_in.expense_id,
                    ExpenseSplit.user_id == settlement_in.payer_id,
                    ExpenseSplit.is_settled.is_(False),
                )
            ).all()

            for split in splits:
                split.is_settled = True
                split.settled_at = settlement_in.transaction_date

        elif settlement_in.status == "completed":
            # 批次結算：標記所有 net_balance >= 0 的成員的 split
            # （而非只標記付款人，因為其他人也可能因本次結算而歸零）
            balances = crud_get_group_balances(db, settlement_in.group_id)

            for b in balances:
                if b.net_balance >= Decimal("0.00"):
                    splits = db.scalars(
                        select(ExpenseSplit)
                        .join(
                            Expense,
                            Expense.id == ExpenseSplit.expense_id,
                        )
                        .where(
                            Expense.group_id == settlement_in.group_id,
                            ExpenseSplit.user_id == b.user_id,
                            ExpenseSplit.is_settled.is_(False),
                        )
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

        group = db.scalar(select(Group).where(Group.id == group_id))
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