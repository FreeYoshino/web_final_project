from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.crud.expense import create_group_expense
from app.db.database import get_db
from app.schemas.expense import ExpenseCreate
from app.services.expense import ExpenseService

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
                    "paid_by_id": "SEED_USER1_ID",
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
                    "paid_by_id": "SEED_USER1_ID",
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
):
    '''
    建立群組費用
    '''
    try:
        expense = create_group_expense(db=db, expense_in=expense_in)
        return {
            "id": str(expense.id),
            "message": "Expense created successfully",
        }
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{group_id}")
def get_expense_list(
    group_id: UUID,
    page: int = Query(
        1,
        ge=1,
        openapi_examples={
            "default_list": {
                "summary": "查詢群組費用列表",
                "description": "使用 path 帶入 group_id，query 帶入 page、size 取得該群組的費用列表。",
                "value": 1,
            },
        },
    ),
    size: int = Query(
        10,
        ge=1,
        openapi_examples={
            "default_list": {
                "summary": "每頁筆數",
                "description": "預設每頁 10 筆。",
                "value": 10,
            },
        },
    ),
    db: Session = Depends(get_db),
):
    '''
    取得群組費用列表
    '''
    try:
        return ExpenseService.get_group_expense_list(
            db=db,
            group_id=group_id,
            page=page,
            size=size,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
