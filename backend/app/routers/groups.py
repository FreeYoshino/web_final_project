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
    UserGroupListResponse,
)

from app.core.security import get_current_user_id

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=UserGroupListResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing token"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)
def get_my_groups(
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
) -> UserGroupListResponse:
    """查詢當前使用者所在的所有群組，包含在每個群組中的角色與成員數"""
    return GroupService.get_my_groups(db, current_user_id)


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
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
) -> GroupBalanceResponse:
    """
    取得指定群組中每個成員的帳務結算餘額
    - **group_id**: 群組的 UUID
    回傳: GroupBalanceResponse 包含每個成員的帳務結算餘額資訊
    錯誤處理:
    - 如果群組不存在 回傳 404 Not Found
    - 其他非預期錯誤回傳 500 Internal Server Error
    """
    return BalanceService.get_group_balances(db, group_id, current_user_id)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=GroupResponse)
def create_group(
    group_in: GroupCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
):
    """建立群組"""
    return GroupService.create_group(db, group_in, current_user_id)


@router.post(
    "/{group_id}/members",
    status_code=status.HTTP_201_CREATED,
    response_model=GroupMemberListResponse,
)
def add_members_to_group(
    group_id: UUID,
    members_in: GroupMembersCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
):
    """加入成員到群組"""
    return GroupService.add_members_to_group(db, group_id, members_in, current_user_id)


@router.get(
    "/{group_id}/members",
    status_code=status.HTTP_200_OK,
    response_model=GroupMemberListResponse,
)
def get_group_members(
    group_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
):
    """取得群組成員清單"""
    return GroupService.get_group_members(db, group_id, current_user_id)
