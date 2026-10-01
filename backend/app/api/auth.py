from fastapi import APIRouter, HTTPException

from app.core.config import DEMO_CASHIER_ID, DEMO_CASHIER_NAME, DEMO_MODE
from app.core.database import database
from app.core.security import create_access_token, password_context
from app.schemas import LoginRequest

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login")
def login(body: LoginRequest):
    if DEMO_MODE:
        if body.cashier_id != DEMO_CASHIER_ID or body.password != "demo1234":
            raise HTTPException(401, "担当者IDまたはパスワードが正しくありません")
        return {"access_token": create_access_token(body.cashier_id), "cashier": {"cashier_id": body.cashier_id, "display_name": DEMO_CASHIER_NAME}}

    with database() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT cashier_id, display_name, password_hash FROM cashiers WHERE cashier_id=%s AND is_active=1", (body.cashier_id,))
            row = cursor.fetchone()
        finally:
            cursor.close()
    if not row or not password_context.verify(body.password, row["password_hash"]):
        raise HTTPException(401, "担当者IDまたはパスワードが正しくありません")
    return {"access_token": create_access_token(row["cashier_id"]), "cashier": {"cashier_id": row["cashier_id"], "display_name": row["display_name"]}}
