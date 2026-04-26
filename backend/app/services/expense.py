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
            
            items.append(
                ExpenseResponse(
                    id=expense.id,
                    description=expense.description,
                    amount=expense.amount,
                    paid_by_id=expense.paid_by_id,
                    group_id=expense.group_id,
                    category=expense.category,
                    split_type=expense.split_type,
                    expense_date=expense.expense_date,
                    created_at=expense.created_at,
                    updated_at=expense.updated_at,
                    payer_name=expense.payer.username,
                    group_name=expense.group.name,
                    settled_amount=settled_amount,
                    pending_amount=pending_amount,
                    splits=[
                        ExpenseSplitSimple(
                            id=split.id,
                            user_id=split.user_id,
                            split_amount=split.split_amount,
                            is_settled=split.is_settled,
                            settled_at=split.settled_at,
                        ) for split in expense.splits
                    ]
                )
            )

        return ExpenseListResponse(
            items=items, total=total, page=page, size=size, pages=pages
        )