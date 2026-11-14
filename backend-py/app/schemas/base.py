from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, PlainSerializer
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base Pydantic model with camelCase serialization and Jackson-like extra='ignore'."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
    )


def serialize_money(v: Any) -> float | None:
    if v is None:
        return None
    if isinstance(v, Decimal):
        return float(v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    return float(v)


def parse_money(v: Any) -> Decimal | None:
    if v is None:
        return None
    if isinstance(v, Decimal):
        return v
    return Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


Money = Annotated[
    Decimal,
    BeforeValidator(parse_money),
    PlainSerializer(serialize_money, return_type=float | None, when_used="json"),
]

LocalDateTime = Annotated[
    datetime,
    PlainSerializer(
        lambda v: v.strftime("%Y-%m-%dT%H:%M:%S") if v is not None else None,
        return_type=str | None,
        when_used="json",
    ),
]

LocalDate = Annotated[
    date,
    PlainSerializer(
        lambda v: v.strftime("%Y-%m-%d") if v is not None else None,
        return_type=str | None,
        when_used="json",
    ),
]


def parse_slot_datetime(v: Any) -> datetime | None:
    if v is None or isinstance(v, datetime):
        return v
    if isinstance(v, str):
        val = v.strip()
        # Accept YYYY-MM-DDTHH:MM:SS, YYYY-MM-DD HH:MM:SS, YYYY-MM-DDTHH:MM, YYYY-MM-DD HH:MM
        val = val.replace(" ", "T")
        if len(val) == 16:  # YYYY-MM-DDTHH:MM
            val = val + ":00"
        return datetime.fromisoformat(val)
    raise ValueError(f"Invalid datetime format: {v}")


SlotDateTime = Annotated[
    datetime,
    BeforeValidator(parse_slot_datetime),
    PlainSerializer(
        lambda v: v.strftime("%Y-%m-%dT%H:%M:%S") if v is not None else None,
        return_type=str | None,
        when_used="json",
    ),
]


def parse_payment_method(v: Any) -> str:
    """Lenient payment method parsing matching PaymentMethod.fromString in Java."""
    if v is None:
        return "BANK_TRANSFER"
    upper = str(v).strip().upper()
    if upper in ("VNPAY", "MOMO", "ZALOPAY", "QR", ""):
        return "BANK_TRANSFER"
    valid = {"WALLET", "BANK_TRANSFER", "CREDIT_CARD", "CASH"}
    if upper in valid:
        return upper
    return "BANK_TRANSFER"


PaymentMethodIn = Annotated[str, BeforeValidator(parse_payment_method)]
