import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from app.core.config import DEMO_CASHIER_ID, DEMO_MODE
from app.core.database import database

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer()


def create_access_token(cashier_id: str) -> str:
    secret = _secret()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=8)
    return jwt.encode({"sub": cashier_id, "exp": expires_at}, secret, algorithm="HS256")


def _secret() -> str:
    secret = os.environ["JWT_SECRET"]
    if secret == "change-me-before-use" or len(secret) < 32:
        raise RuntimeError("JWT_SECRETは32文字以上の固有の値にしてください")
    return secret


def current_cashier(credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]) -> str:
    try:
        payload = jwt.decode(credentials.credentials, _secret(), algorithms=["HS256"], options={"require": ["sub", "exp"]})
        cashier_id = payload["sub"]
    except (jwt.PyJWTError, KeyError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="認証が必要です") from exc
    if DEMO_MODE:
        if cashier_id != DEMO_CASHIER_ID:
            raise HTTPException(status_code=401, detail="認証が必要です")
        return cashier_id
    with database() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT 1 FROM cashiers WHERE cashier_id=%s AND is_active=1", (cashier_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=401, detail="認証が必要です")
        finally:
            cursor.close()
    return cashier_id
