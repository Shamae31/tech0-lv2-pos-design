import unittest
from decimal import Decimal
from unittest.mock import Mock, patch
from uuid import uuid4

from fastapi import HTTPException
from pydantic import ValidationError

from app.api.purchases import _member_discount, create_purchase, quote_purchase
from app.demo_data import TRANSACTIONS
from app.schemas import ConfirmPurchaseRequest, LoginRequest, PurchaseRequest


class PurchaseTests(unittest.TestCase):
    def setUp(self):
        TRANSACTIONS.clear()

    def tearDown(self):
        TRANSACTIONS.clear()

    def test_reject_duplicate_lines_that_bypass_quantity_limit(self):
        with self.assertRaises(ValidationError):
            PurchaseRequest(items=[{"product_code": "X", "quantity": 99}, {"product_code": "X", "quantity": 99}])

    def test_reject_password_beyond_bcrypt_byte_limit(self):
        with self.assertRaises(ValidationError):
            LoginRequest(cashier_id="staff01", password="あ" * 25)

    def test_disabled_rule_is_excluded(self):
        cursor = Mock()
        cursor.fetchone.return_value = None
        self.assertEqual(_member_discount(cursor, 1, Decimal("100"), 1), Decimal("0"))
        self.assertIn("is_active=1", cursor.execute.call_args.args[0])

    def test_negative_discount_is_rejected(self):
        cursor = Mock()
        cursor.fetchone.return_value = {"discount_type": "AMOUNT", "discount_value": Decimal("-10")}
        with self.assertRaises(HTTPException):
            _member_discount(cursor, 1, Decimal("100"), 1)

    @patch("app.api.purchases.DEMO_MODE", True)
    def test_quote_purchase_and_retry_reuses_transaction(self):
        item = {"product_code": "4900000000010", "quantity": 1}
        quote = quote_purchase(PurchaseRequest(items=[item]), "staff01")
        self.assertEqual(quote["grand_total"], Decimal("129"))
        body = ConfirmPurchaseRequest(request_id=uuid4(), expected_grand_total=129, items=[item])
        first = create_purchase(body, "staff01")
        second = create_purchase(body, "staff01")
        self.assertEqual(first["transaction_id"], second["transaction_id"])
        self.assertEqual(len(TRANSACTIONS), 1)

    @patch("app.api.purchases.DEMO_MODE", True)
    def test_changed_total_does_not_save(self):
        body = ConfirmPurchaseRequest(request_id=uuid4(), expected_grand_total=100, items=[{"product_code": "4900000000010", "quantity": 1}])
        with self.assertRaises(HTTPException) as result:
            create_purchase(body, "staff01")
        self.assertEqual(result.exception.status_code, 409)
        self.assertFalse(TRANSACTIONS)
