import math
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session

from app.crud.expense import get_group_expenses
from app.schemas.expense import ExpenseListResponse, ExpenseResponse, ExpenseSplitSimple

class ExpenseService:
    @staticmethod
    def get_group_expense_list(
        db: Session, 
        group_id: UUID, 
        page: int, 
        size: int
    ) -> ExpenseListResponse:
        """
        處理商業邏輯: 計算分頁、計算結算金額、並組裝回傳結構
        """
        if page < 1:
            raise ValueError("page must be greater than 0")
        if size < 1:
            raise ValueError("size must be greater than 0")

        # 計算資料庫 offset
        skip = (page - 1) * size
        
        # 呼叫 CRUD 拿資料
        total, expenses_db = get_group_expenses(
            db=db, group_id=group_id, skip=skip, limit=size
        )
        
        # 計算總頁數
        pages = math.ceil(total / size) if total > 0 else 0
        items = []

        # 資料轉換與金額計算
        for expense in expenses_db:
            settled_amount = sum(
                (split.split_amount for split in expense.splits if split.is_settled),
                Decimal("0.00"),
            )
            pending_amount = sum(
                (split.split_amount for split in expense.splits if not split.is_settled),
                Decimal("0.00"),
            )

            expense_response = ExpenseResponse.model_validate(
                {
                    **expense.__dict__,
                    "payer_name": expense.payer.username,
                    "group_name": expense.group.name,
                    "settled_amount": settled_amount,
                    "pending_amount": pending_amount,
                }
            )
            items.append(expense_response)

        return ExpenseListResponse(
            items=items, total=total, page=page, size=size, pages=pages
        )