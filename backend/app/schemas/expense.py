from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Literal
from decimal import Decimal
from app.schemas.base import BaseSchema, TimestampSchema, IDSchema

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
    
'''Expense的回應schema'''
class ExpenseSplitSimple(BaseSchema):
    '''ExpenseSplit的簡化回應schema'''
    id: UUID
    user_id: UUID
    amount: Decimal
    is_settled: bool
    settled_at: Optional[datetime] = None

class ExpenseResponse(ExpenseBase, TimestampSchema, IDSchema):
    '''Expense的回應schema'''
    
    # 關聯資料
    payer_name: str = Field(..., description="付款人名稱")
    group_name: str = Field(..., description="群組名稱")

    # 分攤明細
    splits: List[ExpenseSplitSimple] = Field(default_factory=list, description="分攤明細列表")

    # 結算欄位
    settled_amount: Decimal = Field(default=Decimal('0.00'), description="已結算金額")
    pending_amount: Decimal = Field(default=Decimal('0.00'), description="未結算金額")

    model_config = ConfigDict(
        **ExpenseBase.model_config,
        json_encoders={
            Decimal: lambda v: f"{v:.2f}",      # 將 Decimal 轉為字串
            datetime: lambda v: v.isoformat(),  # 將 datetime 轉為 ISO 格式字串
        },
    )

class ExpenseListResponse(BaseSchema):
    """Expense 列表回應"""
    items: List[ExpenseResponse]
    total: int
    page: int
    size: int
    pages: int