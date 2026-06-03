from uuid import UUID

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from datetime import datetime, timedelta, timezone

from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError

from app.core.config import get_settings

def create_access_token(data: dict, expires_delta: timedelta = None):
    """生成 JWT access token"""
    settings = get_settings()
    to_encode = data.copy()
    now = datetime.now(timezone.utc)

    # 設定過期時間
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # 加入過期時間和發行時間
    to_encode.update({"exp": expire, "iat": now})

    # 使用設定中的密鑰和算法編碼 JWT
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """驗證 JWT token"""
    settings = get_settings()

    try:
        # 使用設定中的密鑰與算法來解碼並驗證 token（檢查簽章、過期）
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token 已過期",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="無效的 token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
def get_current_user_id(
        token: str = Depends(OAuth2PasswordBearer(tokenUrl="login/")),
):
    payload = verify_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無法辨識使用者",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return UUID(user_id)