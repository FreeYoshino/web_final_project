from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Sequence, Tuple
from uuid import UUID

from sqlalchemy import select, func, exists
from sqlalchemy.orm import Session, selectinload

from app.models.expense import Expense, ExpenseSplit
from app.schemas.expense import ExpenseCreateWithPayer


def create_group_expense(
    db: Session,
    expense_in: ExpenseCreateWithPayer,
    split_amounts: Sequence[Decimal],
) -> Expense:
    """建立一筆群組費用 並同步建立分攤明細"""

    # 建立Expense記錄
    new_expense = Expense(**expense_in.model_dump(exclude={"splits"}))

    # 使用transaction確保Expense和ExpenseSplit的原子性操作
    try:
        db.add(new_expense)
        db.flush()

        split_records = []
        for split_in, split_amount in zip(expense_in.splits, split_amounts):
            is_payer_split = split_in.user_id == expense_in.paid_by_id
            split_records.append(
                ExpenseSplit(
                    expense_id=new_expense.id,
                    user_id=split_in.user_id,
                    split_amount=split_amount,
                    is_settled=is_payer_split,
                    settled_at=datetime.now(timezone.utc) if is_payer_split else None,
                )
            )

        db.add_all(split_records)
        db.commit()
        db.refresh(new_expense)
        return new_expense
    except Exception:
        db.rollback()
        raise


def get_group_expenses(
    db: Session, group_id: UUID, skip: int, limit: int
) -> Tuple[int, Sequence[Expense]]:
    """
    取得群組的歷史帳單列表 (含分頁與關聯資料)
    回傳: (總筆數, 帳單列表)
    """

    # 查詢總筆數
    pending_split_exists = exists().where(
        ExpenseSplit.expense_id == Expense.id,
        ExpenseSplit.is_settled.is_(False),
    )
    total_statements = select(func.count(Expense.id)).where(
        Expense.group_id == group_id,
        pending_split_exists,
    )
    total = db.scalar(total_statements) or 0

    # 取得分頁資料與關聯
    statements = (
        select(Expense)
        .where(
            Expense.group_id == group_id,
            pending_split_exists,
        )
        .options(
            selectinload(Expense.payer),
            selectinload(Expense.group),
            selectinload(Expense.splits),
            selectinload(Expense.splits).selectinload(ExpenseSplit.user),
        )
        .order_by(Expense.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = db.execute(statements)
    expenses = result.scalars().all()

    return total, expenses
