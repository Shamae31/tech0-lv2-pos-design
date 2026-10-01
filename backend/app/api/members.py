from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import DEMO_MEMBER_ID, DEMO_MODE
from app.core.database import database
from app.core.security import current_cashier

router = APIRouter(prefix="/api/members", tags=["members"])


@router.get("/{member_id}")
def get_member(member_id: str, _: Annotated[str, Depends(current_cashier)]):
    if DEMO_MODE:
        if member_id != DEMO_MEMBER_ID:
            raise HTTPException(404, "会員が未登録です")
        return {"member_id": member_id, "name": "デモ会員"}
    with database() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT member_id, name FROM members WHERE member_id=%s AND is_active=1", (member_id,))
            row = cursor.fetchone()
        finally:
            cursor.close()
    if not row:
        raise HTTPException(404, "会員が未登録です")
    return row
