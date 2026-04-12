from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Literal
from decimal import Decimal
from app.schemas.base import BaseSchema, TimestampSchema, IDSchema

# Settlement的付費方式定義
SettlementMethod = Literal["cash", "credit_card", "bank_transfer"]

# Settlement的狀態定義
SettlementStatus = Literal["pending", "completed", "cancelled"]

'''settlement基礎schema'''
class SettlementBase(BaseSchema):
    '''settlement的基礎欄位定義'''
    payer_id: UUID = Field(..., description="付款人ID")
    receiver_id: UUID = Field(..., description="收款人ID")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="交易金額")
    method: Optional[SettlementMethod] = Field(None, description="付款方式")
    status: Optional[SettlementStatus] = Field("pending", description="交易狀態")
    group_id: UUID = Field(..., description="所屬群組ID")
    expense_id: Optional[UUID] = Field(None, description="相關費用ID")
    notes: Optional[str] = Field(None, description="交易備註")
    transaction_date: datetime = Field(..., description="交易日期")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        # 確保金額不會超過 DECIMAL(10, 2) 的限制
        if value > Decimal('99999999.99'):
            raise ValueError('金額超過最大值 99,999,999.99')
        return value

class SettlementCreate(SettlementBase):
    '''建立settlement 時的輸入schema'''
    pass

class SettlementUpdatePUT(SettlementBase):
    '''更新settlement 時的輸入schema'''
    # PUT請求需要提供完整的settlement資料進行替換
    pass

class SettlementUpdatePATCH(BaseSchema):
    '''更新settlement 時的輸入schema'''
    payer_id: Optional[UUID] = None
    receiver_id: Optional[UUID] = None
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    method: Optional[SettlementMethod] = None
    status: Optional[SettlementStatus] = None
    group_id: Optional[UUID] = None
    expense_id: Optional[UUID] = None
    notes: Optional[str] = None
    transaction_date: Optional[datetime] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        if value is not None and value > Decimal('99999999.99'):
            raise ValueError('金額超過最大值 99,999,999.99')
        return value
    
'''settlement的回應schema'''
class SettlementResponse(SettlementBase, TimestampSchema, IDSchema):
    '''settlement的回應schema'''
    
    # 關聯資料
    payer_name: str = Field(..., description="付款人名稱")
    receiver_name: str = Field(..., description="收款人名稱")
    group_name: str = Field(..., description="群組名稱")
    expense_description: Optional[str] = Field(None, description="相關費用描述")

    model_config = ConfigDict(
        **SettlementBase.model_config,
        json_encoders={
            Decimal: lambda v: f'{v:.2f}',      # 將 Decimal 轉為字串
            datetime: lambda v: v.isoformat()   # 將 datetime 轉為 ISO 格式字串
        }
    )   

class SettlementListResponse(BaseSchema):
    '''多筆settlement的回應schema'''
    settlements: List[SettlementResponse]
    total: int
    page: int
    size: int
    pages: int