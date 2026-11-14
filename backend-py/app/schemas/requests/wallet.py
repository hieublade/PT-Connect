from decimal import Decimal

from pydantic import field_validator

from app.schemas.base import CamelModel, Money, PaymentMethodIn


class TopupRequest(CamelModel):
    amount: Money
    payment_method: PaymentMethodIn = "BANK_TRANSFER"

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v is None:
            raise ValueError("Số tiền nạp không được để trống")
        if v < Decimal("10000.00"):
            raise ValueError("Số tiền nạp tối thiểu là 10,000 VND")
        return v


class AdminWithdrawRequest(CamelModel):
    amount: Money
    bank_name: str
    account_number: str
    account_holder: str
    note: str | None = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v is None or v <= Decimal("0.00"):
            raise ValueError("Số tiền rút phải lớn hơn 0 VND")
        return v
