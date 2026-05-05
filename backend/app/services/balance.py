from uuid import UUID
from sqlalchemy.orm import Session

from app.crud.balance import get_group_balances as crud_get_group_balances
from app.schemas.balance import UserBalanceResponse, GroupBalanceResponse 
class BalanceService:
    @staticmethod
    def get_group_balances(db: Session, group_id: UUID) -> GroupBalanceResponse:
        """
        商業邏輯: 從CRUD層獲取餘額資料 將raw_balances 轉化為Pydantic模型並返回
        """
        # 從 CRUD 層獲取原始餘額資料
        raw_balances = crud_get_group_balances(db, group_id)

        # 將 raw_balances 轉化為 Pydantic 模型
        formatted_balances = []
        for balance in raw_balances:
            formatted_balance = {
                "user_id": balance.user_id,
                "total_paid": balance.paid,
                "total_owed": balance.owed,
                "balance": balance.net_balance,
            }
            formatted_balances.append(UserBalanceResponse(**formatted_balance))

        return GroupBalanceResponse(group_id=group_id, balances=formatted_balances)
    