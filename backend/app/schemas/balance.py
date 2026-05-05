from pydantic import Field
from uuid import UUID
from typing import List
from decimal import Decimal
from app.schemas.base import BaseSchema

class UserBalanceResponse(BaseSchema):
    user_id: UUID = Field(..., description="使用者 ID")
    total_paid: Decimal = Field(..., description="該使用者支付的總金額")
    total_owed: Decimal = Field(..., description="該使用者應付的總金額")
    balance: Decimal = Field(..., description="餘額，正數表示該使用者應收款，負數表示該使用者應付款")

class GroupBalanceResponse(BaseSchema):
    group_id: UUID = Field(..., description="群組 ID")
    balances: List[UserBalanceResponse] = Field(..., description="該群組中每個使用者的餘額資訊列表")
