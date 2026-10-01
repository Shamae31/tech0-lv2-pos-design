from decimal import Decimal

PRODUCTS = {
    "4900000000010": {"product_id": 1, "product_code": "4900000000010", "product_name": "ミネラルウォーター", "current_unit_price": Decimal("120"), "tax_rate": Decimal("8"), "image_url": None},
    "4900000000027": {"product_id": 2, "product_code": "4900000000027", "product_name": "食パン", "current_unit_price": Decimal("180"), "tax_rate": Decimal("8"), "image_url": None},
    "4900000000034": {"product_id": 3, "product_code": "4900000000034", "product_name": "日用品", "current_unit_price": Decimal("300"), "tax_rate": Decimal("10"), "image_url": None},
}
TRANSACTIONS: list[dict] = []
