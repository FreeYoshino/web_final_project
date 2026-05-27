from sqlalchemy.orm import Session

from app.crud.settlement import SettlementCrud
from app.models.expense import Expense
from app.models.group import Group, GroupMember
from app.models.settlement import Settlement
from app.models.user import User
from app.schemas.settlement import SettlementCreate

class SettlementService:
    @staticmethod
    def create_settlement(db: Session, settlement_in: SettlementCreate) -> Settlement:
        """
        商業邏輯: 驗證與建立結算記錄
        """
        SettlementService._validate_settlement(db, settlement_in)
        return SettlementCrud.create_settlement(db, settlement_in)

    @staticmethod
    def _validate_settlement(db: Session, settlement_in: SettlementCreate) -> None:
        """建立結算前的商業驗證"""
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
