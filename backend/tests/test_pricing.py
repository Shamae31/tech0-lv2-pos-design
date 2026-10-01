import os
import unittest
from decimal import Decimal

from app.services.pricing import price_line, rounded_tax, summarize


class PricingTests(unittest.TestCase):
    def test_reduced_tax_rounds_down(self):
        os.environ["POS_TAX_ROUNDING"] = "down"
        self.assertEqual(rounded_tax(Decimal("120"), Decimal("8")), Decimal("9"))

    def test_standard_tax(self):
        os.environ["POS_TAX_ROUNDING"] = "down"
        self.assertEqual(rounded_tax(Decimal("300"), Decimal("10")), Decimal("30"))

    def test_half_up_is_configurable(self):
        os.environ["POS_TAX_ROUNDING"] = "half_up"
        self.assertEqual(rounded_tax(Decimal("107"), Decimal("8")), Decimal("9"))

    def test_mixed_tax_summary(self):
        os.environ["POS_TAX_ROUNDING"] = "down"
        lines = [
            price_line(product_name="食品", unit_price=Decimal("120"), quantity=1, tax_rate=Decimal("8")),
            price_line(product_name="日用品", unit_price=Decimal("300"), quantity=1, tax_rate=Decimal("10")),
        ]
        result = summarize(lines)
        self.assertEqual(result["subtotal"], Decimal("420"))
        self.assertEqual(result["tax_total"], Decimal("39"))
        self.assertEqual(result["grand_total"], Decimal("459"))
        self.assertEqual(result["tax_breakdown"]["8"]["tax_amount"], Decimal("9"))


if __name__ == "__main__":
    unittest.main()
