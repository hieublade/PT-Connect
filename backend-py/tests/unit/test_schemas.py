from datetime import date, datetime
from decimal import Decimal

from app.schemas.base import (
    CamelModel,
    LocalDate,
    LocalDateTime,
    Money,
    PaymentMethodIn,
    SlotDateTime,
)


class SampleModel(CamelModel):
    full_name: str
    amount_paid: Money
    session_time: LocalDateTime
    session_date: LocalDate
    optional_value: Money | None = None


class SlotTestModel(CamelModel):
    slot_time: SlotDateTime


class PaymentTestModel(CamelModel):
    method: PaymentMethodIn


def test_camel_model_serialization():
    dt = datetime(2026, 11, 2, 14, 30, 0)
    d = date(2026, 11, 2)
    obj = SampleModel(
        full_name="Nguyen Van A",
        amount_paid=Decimal("500000.50"),
        session_time=dt,
        session_date=d,
    )
    json_data = obj.model_dump(mode="json", by_alias=True)

    # Check camelCase keys
    assert "fullName" in json_data
    assert json_data["fullName"] == "Nguyen Van A"

    assert "amountPaid" in json_data
    assert json_data["amountPaid"] == 500000.5  # JSON float number!
    assert isinstance(json_data["amountPaid"], float)

    assert "sessionTime" in json_data
    assert json_data["sessionTime"] == "2026-11-02T14:30:00"

    assert "sessionDate" in json_data
    assert json_data["sessionDate"] == "2026-11-02"

    assert "optionalValue" in json_data
    assert json_data["optionalValue"] is None


def test_slot_datetime_parsing():
    # ISO format with T
    m1 = SlotTestModel(slotTime="2026-12-01T08:00:00")
    assert m1.slot_time == datetime(2026, 12, 1, 8, 0, 0)

    # Space separator
    m2 = SlotTestModel(slotTime="2026-12-01 08:00:00")
    assert m2.slot_time == datetime(2026, 12, 1, 8, 0, 0)

    # Without seconds
    m3 = SlotTestModel(slotTime="2026-12-01 08:00")
    assert m3.slot_time == datetime(2026, 12, 1, 8, 0, 0)


def test_payment_method_lenient():
    assert PaymentTestModel(method="VNPAY").method == "BANK_TRANSFER"
    assert PaymentTestModel(method="momo").method == "BANK_TRANSFER"
    assert PaymentTestModel(method="zalopay").method == "BANK_TRANSFER"
    assert PaymentTestModel(method="QR").method == "BANK_TRANSFER"
    assert PaymentTestModel(method=None).method == "BANK_TRANSFER"
    assert PaymentTestModel(method="WALLET").method == "WALLET"
    assert PaymentTestModel(method="credit_card").method == "CREDIT_CARD"
    assert PaymentTestModel(method="UNKNOWN_XYZ").method == "BANK_TRANSFER"

def test_clean_certificate_url():
    from app.schemas.certificate import clean_certificate_url
    assert clean_certificate_url(None) is None
    assert clean_certificate_url("") is None
    assert clean_certificate_url("   ") is None
    assert clean_certificate_url("[]") is None
    assert clean_certificate_url('["https://cdn.vn/cert.pdf"]') == "https://cdn.vn/cert.pdf"
    assert clean_certificate_url(["https://cdn.vn/cert1.pdf", "https://cdn.vn/cert2.pdf"]) == "https://cdn.vn/cert1.pdf"
    assert clean_certificate_url("https://cdn.vn/cert.pdf") == "https://cdn.vn/cert.pdf"


def test_register_and_update_pt_certificate_normalization():
    from app.models.enums import Role
    from app.schemas.requests.auth import RegisterRequest
    from app.schemas.requests.pt import UpdatePTProfileRequest

    # Test key certificateUrls with JSON array string
    reg = RegisterRequest(
        fullName="PT Test",
        email="test.pt@example.com",
        password="Password123@",
        phone="0912345678",
        role=Role.PT,
        certificateUrls='["https://cdn.vn/cert.pdf"]',
    )
    assert reg.clean_certificate_url == "https://cdn.vn/cert.pdf"
    assert reg.certificate_url == "https://cdn.vn/cert.pdf"
    assert reg.certificate_urls == "https://cdn.vn/cert.pdf"

    # Test UpdatePTProfileRequest with new key certificateUrl
    upd = UpdatePTProfileRequest(
        availableLocations="Hà Nội",
        certificateUrl="https://cdn.vn/cert_new.pdf",
    )
    assert upd.clean_certificate_url == "https://cdn.vn/cert_new.pdf"
    assert upd.certificate_url == "https://cdn.vn/cert_new.pdf"
    assert upd.certificate_urls == "https://cdn.vn/cert_new.pdf"
