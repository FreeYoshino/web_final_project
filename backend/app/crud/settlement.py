from sqlalchemy.orm import Session

from app.models.user import User
from app.models.group import Group, GroupMember
from app.models.expense import Expense
from app.models.settlement import Settlement
from app.schemas.settlement import SettlementCreate

class SettlementCrud:
    @staticmethod
    def create_settlement(db: Session, settlement_in: SettlementCreate) -> Settlement:
        """建立一筆結算紀錄"""

        # 驗證輸入資料的合理性
        if settlement_in.payer_id == settlement_in.receiver_id:
            raise ValueError("付款人與收款人不能是同一人")

        payer = db.query(User).filter(User.id == settlement_in.payer_id).first()
        if payer is None:
            raise ValueError("付款人不存在")

        receiver = db.query(User).filter(User.id == settlement_in.receiver_id).first()
        if receiver is None:
            raise ValueError("收款人不存在")

        group = db.query(Group).filter(Group.id == settlement_in.group_id).first()
        if group is None:
            raise ValueError("群組不存在")

        payer_in_group = db.query(GroupMember).filter(
            GroupMember.group_id == settlement_in.group_id,
            GroupMember.user_id == settlement_in.payer_id,
        ).first()
        if payer_in_group is None:
            raise ValueError("付款人不是群組成員")

        receiver_in_group = db.query(GroupMember).filter(
            GroupMember.group_id == settlement_in.group_id,
            GroupMember.user_id == settlement_in.receiver_id,
        ).first()
        if receiver_in_group is None:
            raise ValueError("收款人不是群組成員")

        if settlement_in.expense_id is not None:
            expense = db.query(Expense).filter(Expense.id == settlement_in.expense_id).first()
            if expense is None:
                raise ValueError("相關費用不存在")
            if expense.group_id != settlement_in.group_id:
                raise ValueError("相關費用不屬於此群組")

        new_settlement = Settlement(**settlement_in.model_dump())
        try:
            db.add(new_settlement)
            db.commit()
            db.refresh(new_settlement)
            return new_settlement
        except Exception:
            db.rollback()
            raise