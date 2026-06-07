from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.schemas.expense import ExpenseCreate
from app.services.expense import ExpenseService

from app.core.security import get_current_user_id

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_expense(
    # 使用 Body 並提供 openapi_examples 以便在 Swagger UI 中展示範例請求
    expense_in: ExpenseCreate = Body(
        ...,
        openapi_examples={
            "equal_split": {
                "summary": "EQUAL 均分",
                "description": "2 位成員均分 300 元，split_amount 可先填 0 由後端計算。請將 SEED_USER1_ID、SEED_USER2_ID、SEED_GROUP_ID 替換為 seed_data.py 執行後輸出的實際 ID。",
                "value": {
                    "description": "晚餐",
                    "amount": 300,
                    "group_id": "SEED_GROUP_ID",
                    "category": "food",
                    "split_type": "EQUAL",
                    "expense_date": "2026-04-19T18:30:00+08:00",
                    "splits": [
                        {
                            "user_id": "SEED_USER1_ID",
                            "split_amount": 0,
                        },
                        {
                            "user_id": "SEED_USER2_ID",
                            "split_amount": 0,
                        },
                    ],
                },
            },
            "exact_split": {
                "summary": "EXACT 指定金額",
                "description": "2 位成員分攤 120 元，分攤金額總和必須等於 amount。請將 SEED_USER1_ID、SEED_USER2_ID、SEED_GROUP_ID 替換為 seed_data.py 執行後輸出的實際 ID。",
                "value": {
                    "description": "飲料",
                    "amount": 120,
                    "group_id": "SEED_GROUP_ID",
                    "category": "drinks",
                    "split_type": "EXACT",
                    "expense_date": "2026-04-19T19:00:00+08:00",
                    "splits": [
                        {
                            "user_id": "SEED_USER1_ID",
                            "split_amount": 50,
                        },
                        {
                            "user_id": "SEED_USER2_ID",
                            "split_amount": 70,
                        },
                    ],
                },
            },
        },
    ),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
):
    """
    建立群組費用
    """
    expense = ExpenseService.create_group_expense(
        db=db, expense_in=expense_in, current_user_id=current_user_id
    )
    return {
        "id": str(expense.id),
        "message": "Expense created successfully",
    }

