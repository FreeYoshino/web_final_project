from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.group import Group, GroupMember
from app.models.expense import Expense, ExpenseSplit


from uuid import UUID

def get_group_balances(db: Session, group_id: UUID):
    """
    (初步版本: 不包含settlement的邏輯)
    計算群組中每個成員的帳務結算餘額 即他們應該支付或收到的金額
    回傳: List[Dict] 每個成員的帳務結算餘額
    """

    # 驗證輸入資料的合理性
    group = db.query(Group).filter(Group.id == group_id).first() 
    if group is None:
        raise ValueError("群組不存在")
    
    # 子查詢: 計算群組內成員的總代墊金額
    paid_subquery = (
        db.query(
            Expense.paid_by_id.label("user_id"),
            func.sum(Expense.amount).label("total_paid")
        )
        .filter(Expense.group_id == group_id)
        .group_by(Expense.paid_by_id)
        .subquery()
    )

    # 子查詢: 計算群組內成員的應付金額
    owed_subquery = (
        db.query(
            ExpenseSplit.user_id.label("user_id"),
            func.sum(ExpenseSplit.split_amount).label("total_owed")
        )
        .join(Expense, Expense.id == ExpenseSplit.expense_id)
        .filter(Expense.group_id == group_id)
        .group_by(ExpenseSplit.user_id)
        .subquery()
    )

    # 主查詢: 結合代墊金額和應付金額計算每個成員的帳務結算餘額
    balances = (
        db.query(
            GroupMember.user_id,
            func.coalesce(paid_subquery.c.total_paid, 0).label("paid"),
            func.coalesce(owed_subquery.c.total_owed, 0).label("owed"),
            (func.coalesce(paid_subquery.c.total_paid, 0) - func.coalesce(owed_subquery.c.total_owed, 0)).label("net_balance")
        )
        .filter(GroupMember.group_id == group_id)
        .outerjoin(paid_subquery, GroupMember.user_id == paid_subquery.c.user_id)
        .outerjoin(owed_subquery, GroupMember.user_id == owed_subquery.c.user_id)
        .all()
    )

    return balances