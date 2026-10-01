from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class LoginRequest(BaseModel):
    cashier_id: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=72)

    @model_validator(mode="after")
    def check_password_bytes(self):
        if len(self.password.encode("utf-8")) > 72:
            raise ValueError("パスワードが長すぎます")
        return self


class PurchaseItem(BaseModel):
    product_code: str = Field(min_length=1, max_length=64)
    quantity: int = Field(ge=1, le=99)


class PurchaseRequest(BaseModel):
    member_id: str | None = None
    items: list[PurchaseItem] = Field(min_length=1)

    @model_validator(mode="after")
    def check_unique_products(self):
        codes = [item.product_code for item in self.items]
        if len(codes) != len(set(codes)):
            raise ValueError("同じ商品コードは1行にまとめてください")
        return self


class ConfirmPurchaseRequest(PurchaseRequest):
    request_id: UUID
    expected_grand_total: Decimal = Field(ge=0)
