from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.schemas.settlement import SettlementCreate

from app.services.settlement import SettlementService

from app.core.security import get_current_user_id

router = APIRouter(prefix="/settlements", tags=["settlements"])

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error (self-payment, payer/receiver not found)"},
        status.HTTP_403_FORBIDDEN: {"description": "Payer or receiver is not a group member"},
        status.HTTP_404_NOT_FOUND: {"description": "Group not found"},
    },
)
def create_settlement(
    # 使用 Body 並提供 openapi_examples 以便在 Swagger UI 中展示範例請求
    settlement_in: SettlementCreate = Body(
        ...,
        openapi_examples={
            "single_expense": {
                "summary": "針對特定費用的立即還款",
                "description": "當使用者針對某一筆特定的花費（例如昨天的午餐）進行還款時，會帶入 `expense_id`。付款人由 JWT token 自動推斷。",
                "value": {
                    "receiver_id": "請填入對應的receiver_id UUID",
                    "amount": 150.00,
                    "method": "cash",
                    "status": "completed",
                    "group_id": "請填入對應的group_id UUID",
                    "expense_id": "請填入對應的expense_id UUID",
                    "notes": "還昨天的午餐錢",
                    "transaction_date": "2026-05-18T12:30:00Z"
                }
            },
            "batch_settlement": {
                "summary": "總額/批次結清 (無 expense_id)",
                "description": "當使用者進行週期性結算，一次清償多筆墊款的總淨額時，`expense_id` 為 null。付款人由 JWT token 自動推斷。",
                "value": {
                    "receiver_id": "請填入對應的receiver_id UUID",
                    "amount": 1250.50,
                    "method": "bank_transfer",
                    "status": "pending",
                    "group_id": "請填入對應的group_id UUID",
                    "expense_id": None,
                    "notes": "五月份總結算轉帳",
                    "transaction_date": "2026-05-18T13:00:00Z"
                }
            }
        }
    ),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
):
    '''
    建立新的 settlement 記錄
    '''

    # 呼叫 service 層來處理 settlement 的建立邏輯
    settlement = SettlementService.create_settlement(
        db=db, settlement_in=settlement_in, current_user_id=current_user_id
    )

    return {
        "id": str(settlement.id),
        "message": "Settlement created successfully",
    }

