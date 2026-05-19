from pydantic import Field
from uuid import UUID
from typing import List
from decimal import Decimal
from app.schemas.base import BaseSchema

# 定義還款建議模型
class SettlementSuggestion(BaseSchema):
    from_user_id: UUID = Field(..., description="應付款使用者 ID")
    from_user_name: str = Field(..., description="應付款使用者名稱")
    to_user_id: UUID = Field(..., description="應收款使用者 ID")
    to_user_name: str = Field(..., description="應收款使用者名稱")
    amount: Decimal = Field(..., description="建議還款金額")

class UserBalanceResponse(BaseSchema):
    user_id: UUID = Field(..., description="使用者 ID")
    user_name: str = Field(..., description="使用者名稱")
    # 原始 totals（不扣除 settlement）
    total_paid_raw: Decimal = Field(..., description="該使用者支付的總金額（未扣除 settlement）")
    total_owed_raw: Decimal = Field(..., description="該使用者應付的總金額（未扣除 settlement）")
    # settlement 調整量（completed 狀態的結算總額）
    settlements_paid: Decimal = Field(..., description="該使用者作為 payer 已完成的 settlement 總金額")
    settlements_received: Decimal = Field(..., description="該使用者作為 receiver 已完成的 settlement 總金額")
    # 最終淨額（計算公式: total_paid_raw - total_owed_raw + settlements_paid - settlements_received）
    balance: Decimal = Field(..., description="餘額，正數表示該使用者應收款，負數表示該使用者應付款")

class GroupBalanceResponse(BaseSchema):
    group_id: UUID = Field(..., description="群組 ID")
    balances: List[UserBalanceResponse] = Field(..., description="該群組中每個使用者的餘額資訊列表")
    settlements: List[SettlementSuggestion] = Field(..., description="根據目前餘額計算出的還款建議列表")