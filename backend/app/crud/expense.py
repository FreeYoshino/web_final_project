from __future__ import annotations

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func

from app.models.expense import Expense, ExpenseSplit
from app.models.group import Group, GroupMember
from app.models.user import User
from app.schemas.expense import ExpenseCreate
from app.services.expense_split_helper import calculate_split_amounts

from uuid import UUID
from typing import Tuple, Sequence, Optional

def create_group_expense(db: Session, expense_in: ExpenseCreate) -> Expense:
    """建立一筆群組費用 並同步建立分攤明細"""

    # 驗證輸入資料的合理性
    group = db.query(Group).filter(Group.id == expense_in.group_id).first()
    if group is None:
        raise ValueError("群組不存在")

    payer = db.query(User).filter(User.id == expense_in.paid_by_id).first()
    if payer is None:
        raise ValueError("付款人不存在")

    member_ids = {
        member_id
        for (member_id,) in db.query(GroupMember.user_id)
        .filter(GroupMember.group_id == expense_in.group_id)
        .all()
    }
    if not member_ids:
        raise ValueError("群組沒有任何成員")

    if expense_in.paid_by_id not in member_ids:
        raise ValueError("付款人不是群組成員")

    split_user_ids = [split.user_id for split in expense_in.splits]
    if len(split_user_ids) != len(set(split_user_ids)):
        raise ValueError("分攤明細中包含重複使用者")

    if any(user_id not in member_ids for user_id in split_user_ids):
        raise ValueError("分攤明細中包含非群組成員")

    # 計算分攤金額
    split_amounts = calculate_split_amounts(
        amount=expense_in.amount,
        split_type=expense_in.split_type,
        splits=expense_in.splits,
    )

    # 建立Expense記錄
    new_expense = Expense(**expense_in.model_dump(exclude={"splits"}))

    # 使用transaction確保Expense和ExpenseSplit的原子性操作
    try:
        db.add(new_expense)
        db.flush()

        split_records = []
        for split_in, split_amount in zip(expense_in.splits, split_amounts):
            split_records.append(
                ExpenseSplit(
                    expense_id=new_expense.id,
                    user_id=split_in.user_id,
                    split_amount=split_amount,
                )
            )

        db.add_all(split_records)
        db.commit()
        db.refresh(new_expense)
        return new_expense
    except Exception:
        db.rollback()
        raise

def get_group_expenses(db: Session, group_id: UUID, skip: int, limit: int) -> Tuple[int, Sequence[Expense]]:
    """
    取得群組的歷史帳單列表 (含分頁與關聯資料)
    回傳: (總筆數, 帳單列表)
    """

    # 驗證群組存在
    group = db.query(Group).filter(Group.id == group_id).first() 
    if group is None:
        raise ValueError("群組不存在")
    
    # 查詢總筆數
    total_statements = select(func.count(Expense.id)).where(Expense.group_id == group_id)
    total = db.scalar(total_statements)

    # 取得分頁資料與關聯
    statements = (
        select(Expense)
        .where(Expense.group_id == group_id)
        .options(
            selectinload(Expense.payer),
            selectinload(Expense.group),
            selectinload(Expense.splits)
        )
        .order_by(Expense.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = db.execute(statements)
    expenses = result.scalars().all()
    
    return total, expenses