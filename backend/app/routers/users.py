from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
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
