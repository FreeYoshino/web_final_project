from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.group import Group, GroupMember
from app.models.expense import Expense, ExpenseSplit
from app.models.settlement import Settlement
from app.models.user import User
from uuid import UUID


def get_group_balances(db: Session, group_id: UUID):
    """
    (版本2: 添加settlement的邏輯)
    計算群組中每個成員的帳務結算餘額 即他們應該支付或收到的金額
    公式: net_balance = paid - owed + paid_settlements - received_settlements
    回傳: List[Dict] 每個成員的帳務結算餘額
    """

    # 子查詢: 計算群組內成員的總代墊金額
    paid_subquery = (
        select(
            Expense.paid_by_id.label("user_id"),
            func.sum(Expense.amount).label("total_paid"),
        )
        .where(Expense.group_id == group_id)
        .group_by(Expense.paid_by_id)
        .subquery()
    )

    # 子查詢: 計算群組內成員的應付金額
    owed_subquery = (
        select(
            ExpenseSplit.user_id.label("user_id"),
            func.sum(ExpenseSplit.split_amount).label("total_owed"),
        )
        .join(Expense, Expense.id == ExpenseSplit.expense_id)
        .where(Expense.group_id == group_id)
        .group_by(ExpenseSplit.user_id)
        .subquery()
    )

    # 子查詢: 計算群組內成員作為付款人的總settlement金額
    paid_settlement_subquery = (
        select(
            Settlement.payer_id.label("user_id"),
            func.sum(Settlement.amount).label("total_paid_settlement"),
        )
        .where(
            Settlement.group_id == group_id,
            Settlement.status == "completed",
        )
        .group_by(Settlement.payer_id)
        .subquery()
    )

    # 子查詢: 計算群組內成員作為收款人的總settlement金額
    received_settlement_subquery = (
        select(
            Settlement.receiver_id.label("user_id"),
            func.sum(Settlement.amount).label("total_received_settlement"),
        )
        .where(
            Settlement.group_id == group_id,
            Settlement.status == "completed",
        )
        .group_by(Settlement.receiver_id)
        .subquery()
    )

    # 主查詢: 結合代墊金額、應付金額和settlement金額計算每個成員的帳務結算餘額
    # 公式: net_balance = paid - owed + paid_settlement - received_settlement
    balances = db.execute(
        select(
            GroupMember.user_id,
            User.name.label("user_name"),
            func.coalesce(paid_subquery.c.total_paid, 0).label("paid"),
            func.coalesce(owed_subquery.c.total_owed, 0).label("owed"),
            func.coalesce(paid_settlement_subquery.c.total_paid_settlement, 0).label(
                "paid_settlement"
            ),
            func.coalesce(
                received_settlement_subquery.c.total_received_settlement, 0
            ).label("received_settlement"),
            (
                func.coalesce(paid_subquery.c.total_paid, 0)
                - func.coalesce(owed_subquery.c.total_owed, 0)
                + func.coalesce(paid_settlement_subquery.c.total_paid_settlement, 0)
                - func.coalesce(
                    received_settlement_subquery.c.total_received_settlement, 0
                )
            ).label("net_balance"),
        )
        .select_from(GroupMember)
        .join(User, GroupMember.user_id == User.id)
        .outerjoin(paid_subquery, GroupMember.user_id == paid_subquery.c.user_id)
        .outerjoin(owed_subquery, GroupMember.user_id == owed_subquery.c.user_id)
        .outerjoin(
            paid_settlement_subquery,
            GroupMember.user_id == paid_settlement_subquery.c.user_id,
        )
        .outerjoin(
            received_settlement_subquery,
            GroupMember.user_id == received_settlement_subquery.c.user_id,
        )
        .where(GroupMember.group_id == group_id)
    )

    return balances.all()
