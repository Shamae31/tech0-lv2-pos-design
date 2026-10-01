import hashlib
import json
import logging
from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN
from typing import Annotated

import mysql.connector
from fastapi import APIRouter, Depends, HTTPException

from app.core.config import DEMO_CASHIER_NAME, DEMO_MEMBER_ID, DEMO_MODE
from app.core.database import database
from app.core.security import current_cashier
from app.demo_data import PRODUCTS, TRANSACTIONS
from app.schemas import ConfirmPurchaseRequest, PurchaseRequest
from app.services.pricing import PricedLine, price_line, summarize

router = APIRouter(prefix="/api/purchases", tags=["purchases"])
logger = logging.getLogger(__name__)


def _member_discount(cursor, product_id: int, unit_price: Decimal, quantity: int) -> Decimal:
    cursor.execute("""SELECT discount_type, discount_value FROM promotion_rules WHERE product_id=%s
        AND is_active=1 AND applicable_from<=NOW() AND (applicable_to IS NULL OR applicable_to>=NOW())
        ORDER BY applicable_from DESC LIMIT 1""", (product_id,))
    rule = cursor.fetchone()
    if not rule:
        return Decimal("0")
    value = Decimal(rule["discount_value"])
    if value < 0 or (rule["discount_type"] == "RATE" and value > 100):
        raise HTTPException(409, "割引設定が不正です")
    gross = unit_price * quantity
    discount = gross * value / Decimal("100") if rule["discount_type"] == "RATE" else value * quantity
    return min(gross, discount.quantize(Decimal("1"), rounding=ROUND_DOWN))


def _calculate(body: PurchaseRequest, cursor=None, *, lock: bool = False):
    if DEMO_MODE and body.member_id and body.member_id != DEMO_MEMBER_ID:
        raise HTTPException(400, "会員が未登録です")
    if not DEMO_MODE and body.member_id:
        cursor.execute("SELECT member_id FROM members WHERE member_id=%s AND is_active=1", (body.member_id,))
        if not cursor.fetchone():
            raise HTTPException(400, "会員が未登録です")

    lines: list[tuple[int, str, PricedLine]] = []
    for item in body.items:
        if DEMO_MODE:
            product = PRODUCTS.get(item.product_code)
        else:
            cursor.execute("""SELECT p.product_id, p.product_name, p.current_unit_price, tr.tax_rate
                FROM products p JOIN tax_rates tr ON tr.tax_category_id=p.tax_category_id
                AND tr.applicable_from<=NOW() AND (tr.applicable_to IS NULL OR tr.applicable_to>=NOW())
                WHERE p.product_code=%s AND p.is_active=1 ORDER BY tr.applicable_from DESC LIMIT 1""" + (" FOR UPDATE" if lock else ""), (item.product_code,))
            product = cursor.fetchone()
        if not product:
            raise HTTPException(400, f"商品が未登録です: {item.product_code}")
        discount = _member_discount(cursor, product["product_id"], product["current_unit_price"], item.quantity) if body.member_id and not DEMO_MODE else Decimal("0")
        line = price_line(product_name=product["product_name"], unit_price=Decimal(product["current_unit_price"]), quantity=item.quantity, tax_rate=Decimal(product["tax_rate"]), discount=discount)
        lines.append((product["product_id"], item.product_code, line))
    totals = summarize([line for _, _, line in lines])
    return lines, totals


@router.post("/quote")
def quote_purchase(body: PurchaseRequest, _: Annotated[str, Depends(current_cashier)]):
    if DEMO_MODE:
        lines, totals = _calculate(body)
    else:
        with database() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                lines, totals = _calculate(body, cursor)
            finally:
                cursor.close()
    return {**totals, "details": [{"product_code": code, **line} for _, code, line in lines]}


def _request_hash(body: ConfirmPurchaseRequest, cashier_id: str) -> str:
    payload = {"cashier_id": cashier_id, "member_id": body.member_id, "items": [item.model_dump() for item in body.items], "expected_grand_total": str(body.expected_grand_total)}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _existing_purchase(cursor, request_id: str, request_hash: str):
    cursor.execute("SELECT transaction_id, request_hash, member_id, subtotal, tax_total, grand_total FROM transactions WHERE request_id=%s", (request_id,))
    row = cursor.fetchone()
    if not row:
        return None
    if row["request_hash"] != request_hash:
        raise HTTPException(409, "購入要求IDが別の内容に使われています")
    cursor.execute("SELECT applied_tax_rate, SUM(line_total) taxable_amount, SUM(tax_amount) tax_amount FROM transaction_details WHERE transaction_id=%s GROUP BY applied_tax_rate", (row["transaction_id"],))
    breakdown = {format(Decimal(line["applied_tax_rate"]).normalize(), "f"): {"taxable_amount": line["taxable_amount"], "tax_amount": line["tax_amount"]} for line in cursor.fetchall()}
    return {"transaction_id": row["transaction_id"], "member_id": row["member_id"], "subtotal": row["subtotal"], "tax_total": row["tax_total"], "grand_total": row["grand_total"], "tax_breakdown": breakdown}


@router.post("")
def create_purchase(body: ConfirmPurchaseRequest, cashier_id: Annotated[str, Depends(current_cashier)]):
    request_id = str(body.request_id)
    request_hash = _request_hash(body, cashier_id)
    if DEMO_MODE:
        for transaction in TRANSACTIONS:
            if transaction.get("request_id") == request_id:
                if transaction["request_hash"] != request_hash:
                    raise HTTPException(409, "購入要求IDが別の内容に使われています")
                return {key: value for key, value in transaction.items() if key not in ("request_id", "request_hash")}
        lines, totals = _calculate(body)
        if totals["grand_total"] != body.expected_grand_total:
            raise HTTPException(409, "金額が更新されました。内容を確認してください")
        result = {"request_id": request_id, "request_hash": request_hash, "transaction_id": f"DEMO-{len(TRANSACTIONS) + 1:03d}", "purchased_at": datetime.now(timezone.utc).isoformat(), "cashier_name": DEMO_CASHIER_NAME, "member_id": body.member_id, **totals, "details": [{"product_code": code, **line} for _, code, line in lines]}
        TRANSACTIONS.insert(0, result)
        return {key: value for key, value in result.items() if key not in ("request_id", "request_hash")}

    with database() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            connection.start_transaction()
            existing = _existing_purchase(cursor, request_id, request_hash)
            if existing:
                connection.rollback()
                return existing
            lines, totals = _calculate(body, cursor, lock=True)
            if totals["grand_total"] != body.expected_grand_total:
                raise HTTPException(409, "金額が更新されました。内容を確認してください")
            cursor.execute("INSERT INTO transactions(request_id, request_hash, member_id, cashier_id, subtotal, tax_total, grand_total) VALUES(%s,%s,%s,%s,%s,%s,%s)", (request_id, request_hash, body.member_id or None, cashier_id, totals["subtotal"], totals["tax_total"], totals["grand_total"]))
            transaction_id = cursor.lastrowid
            cursor.executemany("INSERT INTO transaction_details(transaction_id, product_id, quantity, sold_unit_price, discount_amount, applied_tax_rate, tax_amount, line_total) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)", [(transaction_id, product_id, line["quantity"], line["sold_unit_price"], line["discount_amount"], line["applied_tax_rate"], line["tax_amount"], line["line_total"]) for product_id, _, line in lines])
            connection.commit()
            return {"transaction_id": transaction_id, "member_id": body.member_id, **totals}
        except mysql.connector.IntegrityError as exc:
            connection.rollback()
            if exc.errno == 1062:
                existing = _existing_purchase(cursor, request_id, request_hash)
                if existing:
                    return existing
            logger.exception("Purchase database integrity error")
            raise HTTPException(503, "データベース処理に失敗しました") from exc
        except HTTPException:
            connection.rollback()
            raise
        except mysql.connector.Error as exc:
            connection.rollback()
            logger.exception("Purchase database error")
            raise HTTPException(503, "データベース処理に失敗しました") from exc
        finally:
            cursor.close()
