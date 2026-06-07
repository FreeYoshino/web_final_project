from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserSearchResponse
from app.schemas.jwt import Token
from app.services.user import UserService

router = APIRouter(prefix="", tags=["users"])

@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(
		user_in: UserCreate = Body(
			...,
			openapi_examples={
				"default_user": {
					"summary": "建立使用者範例",
					"description": "建立一筆新的使用者資料，請依實際需求替換 email、username、name、password。",
					"value": {
						"username": "alice",
						"email": "alice@example.com",
						"phone": "0912345678",
						"name": "Alice Chen",
						"password": "password123",
					},
				},
			},
		),
		db: Session = Depends(get_db),
):
		"""建立使用者"""
		try:
			return UserService.create_user(db=db, user_in=user_in)
		except ValueError as exc:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get(
		"/users/me",
		status_code=status.HTTP_200_OK,
		response_model=UserResponse,
		responses={
			status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing token"},
			status.HTTP_404_NOT_FOUND: {"description": "User not found"},
		},
)
def get_current_user(
		db: Session = Depends(get_db),
		current_user_id: UUID = Depends(get_current_user_id),
) -> UserResponse:
		"""查詢目前已登入的使用者資料（從 JWT token 推斷身分）"""
		user = db.scalar(select(User).where(User.id == current_user_id))
		if user is None:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND, detail="使用者不存在"
			)
		return UserResponse.model_validate(user)


@router.post(
		"/login",
		status_code=status.HTTP_200_OK,
		response_model=Token,
		responses={
			status.HTTP_401_UNAUTHORIZED: {"description": "密碼錯誤"},
			status.HTTP_404_NOT_FOUND: {"description": "使用者不存在或信箱錯誤"},
		},
		openapi_extra={
			"requestBody": {
				"required": True,
				"description": "OAuth2 Password Grant 表單。username 請填使用者 email，password 請填登入密碼。",
				"content": {
					"application/x-www-form-urlencoded": {
						"example": {
							"username": "alice@example.com",
							"password": "password123",
						},
					},
				},
			},
		},
)
def login_user(
		form_data: OAuth2PasswordRequestForm = Depends(),
		db: Session = Depends(get_db),
):
		"""
		使用者登入成功後回傳 JWT access token。
		注意: OAuth2PasswordRequestForm 的 username 欄位請填使用者 email 而非 username
		"""
		return UserService.authenticate_user(db=db, email=form_data.username, password=form_data.password)


@router.get(
    "/users",
    status_code=status.HTTP_200_OK,
    response_model=UserSearchResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "搜尋關鍵字不可為空白"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing token"},
        status.HTTP_404_NOT_FOUND: {"description": "指定的群組不存在"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)
def search_users(
    q: str = Query(
        ...,
        min_length=1,
        max_length=50,
        description="搜尋關鍵字（必填，比對 username 或 name，不區分大小寫）。此端點僅支援搜尋，不支援無條件列出所有使用者。",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=50,
        description="回傳筆數上限",
    ),
    exclude_group_id: UUID | None = Query(
        None,
        description="排除已在此群組中的使用者（用於邀請加入群組時過濾既有成員）",
    ),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
) -> UserSearchResponse:
    """
    搜尋使用者（需要登入）

    根據關鍵字模糊比對 username 或 name，回傳符合條件的使用者清單。
    - 自動排除搜尋者本人（避免重複加入群組）
    - 可選擇排除已存在於特定群組中的成員
    - 搜尋結果只包含 id、username、name，不暴露 email、phone 等隱私欄位
    """
    return UserService.search_users(
        db=db,
        query=q,
        limit=limit,
        exclude_group_id=exclude_group_id,
        current_user_id=current_user_id,
    )
