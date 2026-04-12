from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Literal
from decimal import Decimal
from .base import BaseSchema

# Split 類型定義
SplitType = Literal["EQUAL", "EXACT"]

'''Expense基礎schema'''
class ExpenseBase(BaseSchema):
    '''Expense的基礎欄位定義'''
    description: str = Field(..., min_length=1, max_length=255, description="費用描述")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="費用金額")
    paid_by_id: UUID = Field(..., description="付款人ID")
    group_id: UUID = Field(..., description="群組ID")
    category: Optional[str] = Field(None, max_length=50, description="費用類別")
    split_type: SplitType = Field(default="EQUAL", description="分帳类型")
    expense_date: datetime = Field(..., description="費用發生日期")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        # 確保金額不會超過 DECIMAL(10, 2) 的限制
        if value > Decimal('99999999.99'):
            raise ValueError('金額超過最大值 99,999,999.99')
        return value

class ExpenseCreate(ExpenseBase):
    '''建立Expense 時的輸入schema'''
    pass

class ExpenseUpdatetPUT(ExpenseBase):
    '''更新Expense 時的輸入schema'''
    # PUT請求需要提供完整的Expense資料進行替換
    pass

class ExpenseUpdatePATCH(BaseSchema):
    '''更新Expense 時的輸入schema'''
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    paid_by_id: Optional[UUID] = None
    group_id: Optional[UUID] = None
    split_type: Optional[SplitType] = None
    expense_date: Optional[datetime] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        if value is not None and value > Decimal('99999999.99'):
            raise ValueError('金額超過最大值 99,999,999.99')
        return value
