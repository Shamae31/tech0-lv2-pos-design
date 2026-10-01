from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.config import DEMO_MODE
from app.core.database import database
from app.core.security import current_cashier
from app.demo_data import TRANSACTIONS

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("")
def list_transactions(_: Annotated[str, Depends(current_cashier)], page: int = Query(0, ge=0)):
    if DEMO_MODE:
        return [{key: value for key, value in row.items() if key not in ("request_id", "request_hash")} for row in TRANSACTIONS[page * 50:(page + 1) * 50]]
    with database() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT transaction_id FROM transactions ORDER BY purchased_at DESC, transaction_id DESC LIMIT 50 OFFSET %s", (page * 50,))
            transaction_ids = [row["transaction_id"] for row in cursor.fetchall()]
            if not transaction_ids:
                return []
            placeholders = ",".join(["%s"] * len(transaction_ids))
            cursor.execute(f"""SELECT t.transaction_id, t.purchased_at, t.member_id, c.display_name cashier_name,
                t.subtotal, t.tax_total, t.grand_total, d.detail_id, p.product_name, d.quantity,
                d.sold_unit_price, d.discount_amount, d.applied_tax_rate, d.tax_amount, d.line_total
                FROM transactions t JOIN cashiers c ON c.cashier_id=t.cashier_id
                JOIN transaction_details d ON d.transaction_id=t.transaction_id
                JOIN products p ON p.product_id=d.product_id
                WHERE t.transaction_id IN ({placeholders})
                ORDER BY t.purchased_at DESC, t.transaction_id DESC, d.detail_id""", transaction_ids)
            rows = cursor.fetchall()
        finally:
            cursor.close()
    grouped = {}
    for row in rows:
        transaction_id = row["transaction_id"]
        transaction = grouped.setdefault(transaction_id, {"transaction_id": transaction_id, "purchased_at": row["purchased_at"], "member_id": row["member_id"], "cashier_name": row["cashier_name"], "subtotal": row["subtotal"], "tax_total": row["tax_total"], "grand_total": row["grand_total"], "details": []})
        transaction["details"].append({key: row[key] for key in ("product_name", "quantity", "sold_unit_price", "discount_amount", "applied_tax_rate", "tax_amount", "line_total")})
    return list(grouped.values())
