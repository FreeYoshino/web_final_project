from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.services.balance import BalanceService
from app.db.database import get_db
from app.schemas.balance import GroupBalanceResponse

router = APIRouter(prefix="/groups", tags=["groups"])

@router.get(
    "/{group_id}/balances",
    status_code=status.HTTP_200_OK,
    response_model=GroupBalanceResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Group not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)
def get_group_balances(
    group_id: UUID,
    db: Session = Depends(get_db),
) -> GroupBalanceResponse:
    """
    取得指定群組中每個成員的帳務結算餘額
    - **group_id**: 群組的 UUID
    回傳: GroupBalanceResponse 包含每個成員的帳務結算餘額資訊
    錯誤處理:
    - 如果群組不存在 回傳 404 Not Found
    - 其他非預期錯誤回傳 500 Internal Server Error
    """
    try:
        # 呼叫 service 層計算並獲取該群組的餘額資訊
        return BalanceService.get_group_balances(db, group_id)
    except ValueError as exc:
        # 例如群組不存在這類可預期的業務錯誤
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        # 非預期錯誤回傳 500，避免誤導為客戶端請求錯誤
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc
    