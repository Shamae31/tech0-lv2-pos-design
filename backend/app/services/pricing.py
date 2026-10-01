import os
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from typing import TypedDict


class PricedLine(TypedDict):
    product_name: str
    quantity: int
    sold_unit_price: Decimal
    discount_amount: Decimal
    applied_tax_rate: Decimal
    tax_amount: Decimal
    line_total: Decimal


def rounded_tax(net: Decimal, rate: Decimal) -> Decimal:
    """Calculate tax using the configured rounding rule."""
    rounding = ROUND_HALF_UP if os.getenv("POS_TAX_ROUNDING", "down") == "half_up" else ROUND_DOWN
    return (net * rate / Decimal("100")).quantize(Decimal("1"), rounding=rounding)


def price_line(*, product_name: str, unit_price: Decimal, quantity: int, tax_rate: Decimal, discount: Decimal = Decimal("0")) -> PricedLine:
    line_total = unit_price * quantity - discount
    return {
        "product_name": product_name,
        "quantity": quantity,
        "sold_unit_price": unit_price,
        "discount_amount": discount,
        "applied_tax_rate": tax_rate,
        "tax_amount": rounded_tax(line_total, tax_rate),
        "line_total": line_total,
    }


def summarize(lines: list[PricedLine]) -> dict:
    subtotal = sum((line["line_total"] for line in lines), Decimal("0"))
    tax_total = sum((line["tax_amount"] for line in lines), Decimal("0"))
    tax_breakdown: dict[str, dict[str, Decimal]] = {}
    for line in lines:
        key = format(line["applied_tax_rate"].normalize(), "f")
        bucket = tax_breakdown.setdefault(key, {"taxable_amount": Decimal("0"), "tax_amount": Decimal("0")})
        bucket["taxable_amount"] += line["line_total"]
        bucket["tax_amount"] += line["tax_amount"]
    return {"subtotal": subtotal, "tax_total": tax_total, "grand_total": subtotal + tax_total, "tax_breakdown": tax_breakdown}
