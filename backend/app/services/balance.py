from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.group import Group, GroupMember

from app.crud.balance import get_group_balances as crud_get_group_balances
from app.schemas.balance import UserBalanceResponse, GroupBalanceResponse

from app.services.simplification import simplify_debts


class BalanceService:
    @staticmethod
    def get_group_balances(
        db: Session, group_id: UUID, current_user_id: UUID
    ) -> GroupBalanceResponse:
        """
        商業邏輯: 從CRUD層獲取餘額資料 將raw_balances 轉化為Pydantic模型並返回
        """

        # 驗證輸入資料的合理性
        group = db.scalar(select(Group).where(Group.id == group_id))
        if group is None:
            raise ValueError("群組不存在")

        current_user_in_group = db.scalar(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == current_user_id,
            )
        )
        if current_user_in_group is None:
            raise ValueError("使用者不是群組成員")

        # 從 CRUD 層獲取原始餘額資料
        raw_balances = crud_get_group_balances(db, group_id)

        # 將 raw_balances 轉化為 Pydantic 模型 (回傳原始 totals 與 settlement 調整量)
        formatted_balances = []
        for balance in raw_balances:
            formatted_balances.append(
                UserBalanceResponse.model_validate(
                    {
                        "user_id": balance.user_id,
                        "user_name": balance.user_name,
                        "total_paid_raw": balance.paid,
                        "total_owed_raw": balance.owed,
                        "settlements_paid": getattr(balance, "paid_settlement", 0),
                        "settlements_received": getattr(
                            balance, "received_settlement", 0
                        ),
                        "balance": balance.net_balance,
                    }
                )
            )

        # 計算簡化後的交易建議
        settlements = simplify_debts(formatted_balances)

        return GroupBalanceResponse.model_validate(
            {
                "group_id": group_id,
                "balances": formatted_balances,
                "settlements": settlements,
            }
        )
