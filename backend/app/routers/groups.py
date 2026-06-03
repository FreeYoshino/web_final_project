from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.services.balance import BalanceService
from app.services.group import GroupService
from app.db.database import get_db
from app.schemas.balance import GroupBalanceResponse
from app.schemas.group import (
    GroupCreate,
    GroupResponse,
    GroupMembersCreate,
    GroupMemberListResponse,
)

from app.core.security import get_current_user_id

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get(
    "/{group_id}/balances",
    status_code=status.HTTP_200_OK,
    response_model=GroupBalanceResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Group not found"},
        status.HTTP_403_FORBIDDEN: {"description": "User is not a group member"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)
def get_group_balances(
    group_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
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
        return BalanceService.get_group_balances(db, group_id, current_user_id)
    except ValueError as exc:
        # 例如群組不存在這類可預期的業務錯誤
        if str(exc) == "使用者不是群組成員":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except Exception as exc:
        # 非預期錯誤回傳 500，避免誤導為客戶端請求錯誤
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc


@router.post("", status_code=status.HTTP_201_CREATED, response_model=GroupResponse)
def create_group(
    group_in: GroupCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
):
    """建立群組"""
    try:
        return GroupService.create_group(db, group_in, current_user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@router.post(
    "/{group_id}/members",
    status_code=status.HTTP_201_CREATED,
    response_model=GroupMemberListResponse,
)
def add_members_to_group(
    group_id: UUID,
    members_in: GroupMembersCreate,
    db: Session = Depends(get_db),
):
    """加入成員到群組"""
    try:
        return GroupService.add_members_to_group(db, group_id, members_in)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@router.get(
    "/{group_id}/members",
    status_code=status.HTTP_200_OK,
    response_model=GroupMemberListResponse,
)
def get_group_members(
    group_id: UUID,
    db: Session = Depends(get_db),
):
    """取得群組成員清單"""
    try:
        return GroupService.get_group_members(db, group_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
