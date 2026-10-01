from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import DEMO_MODE
from app.core.database import database
from app.core.security import current_cashier
from app.demo_data import PRODUCTS

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/{code}")
def get_product(code: str, _: Annotated[str, Depends(current_cashier)]):
    if DEMO_MODE:
        row = PRODUCTS.get(code)
        if not row:
            raise HTTPException(404, "商品が未登録です")
        return row
    with database() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""SELECT p.product_id, p.product_code, p.product_name, p.current_unit_price, p.image_url, tr.tax_rate
                FROM products p JOIN tax_rates tr ON tr.tax_category_id=p.tax_category_id
                AND tr.applicable_from<=NOW() AND (tr.applicable_to IS NULL OR tr.applicable_to>=NOW())
                WHERE p.product_code=%s AND p.is_active=1 ORDER BY tr.applicable_from DESC LIMIT 1""", (code,))
            row = cursor.fetchone()
        finally:
            cursor.close()
    if not row:
        raise HTTPException(404, "商品が未登録です")
    return row
