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


class WithdrawRequest(CamelModel):
    amount: Money
    bank_name: str = "Vietcombank"
    account_number: str = ""
    account_name: str = ""

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v is None:
            raise ValueError("Số tiền rút không được để trống")
        if v < Decimal("50000.00"):
            raise ValueError("Số tiền rút tối thiểu là 50,000 VND")
        return v

    @field_validator("account_number")
    @classmethod
    def validate_account_number(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("Số tài khoản nhận tiền không được để trống")
        return v

