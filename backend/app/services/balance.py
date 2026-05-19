from uuid import UUID
from sqlalchemy.orm import Session

from app.crud.balance import get_group_balances as crud_get_group_balances
from app.schemas.balance import UserBalanceResponse, GroupBalanceResponse 

from app.services.simplification import simplify_debts

class BalanceService:
    @staticmethod
    def get_group_balances(db: Session, group_id: UUID) -> GroupBalanceResponse:
        """
        商業邏輯: 從CRUD層獲取餘額資料 將raw_balances 轉化為Pydantic模型並返回
        """
        # 從 CRUD 層獲取原始餘額資料
        raw_balances = crud_get_group_balances(db, group_id)

        # 將 raw_balances 轉化為 Pydantic 模型 (回傳原始 totals 與 settlement 調整量)
        formatted_balances = []
        for balance in raw_balances:
            formatted_balance = {
                "user_id": balance.user_id,
                "user_name": balance.user_name,
                "total_paid_raw": balance.paid,
                "total_owed_raw": balance.owed,
                "settlements_paid": getattr(balance, 'paid_settlement', 0),
                "settlements_received": getattr(balance, 'received_settlement', 0),
                "balance": balance.net_balance,
            }
            formatted_balances.append(UserBalanceResponse(**formatted_balance))

        # 計算簡化後的交易建議
        settlements = simplify_debts(formatted_balances)

        return GroupBalanceResponse(group_id=group_id, balances=formatted_balances, settlements=settlements)
    