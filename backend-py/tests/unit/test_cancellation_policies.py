from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.models.availability_slot import AvailabilitySlot
from app.models.booking import Booking
from app.models.enums import BookingStatus, BookingType, Role
from app.policies.factory import CancellationPolicyFactory

SESSION_FEE = Decimal("300000.00")


@pytest.fixture
def factory():
    return CancellationPolicyFactory()


def create_booking(booking_type: BookingType, status: BookingStatus, slot_start: datetime) -> Booking:
    slot = AvailabilitySlot(
        start_time=slot_start,
        end_time=slot_start + timedelta(hours=1),
    )
    return Booking(
        id=100,
        booking_type=booking_type,
        status=status,
        session_fee=SESSION_FEE,
        slot=slot,
    )


def test_student_cancel_pending(factory):
    now = datetime(2026, 11, 2, 10, 0, 0)
    slot_time = now + timedelta(hours=48)
    booking = create_booking(BookingType.PACKAGE, BookingStatus.PENDING, slot_time)

    policy = factory.get_policy(Role.STUDENT)
    result = policy.calculate(booking, now, "Bận việc đột xuất", None)

    assert result.restore_session is True
    assert result.refund_amount == SESSION_FEE
    assert result.compensation_amount == Decimal("0.00")
    assert result.penalty_amount == Decimal("0.00")


def test_student_cancel_confirmed_advance_notice(factory):
    now = datetime(2026, 11, 2, 10, 0, 0)
    slot_time = now + timedelta(hours=25)
    booking = create_booking(BookingType.PACKAGE, BookingStatus.CONFIRMED, slot_time)

    policy = factory.get_policy(Role.STUDENT)
    result = policy.calculate(booking, now, "Có kế hoạch khác", None)

    assert result.restore_session is True
    assert result.refund_amount == SESSION_FEE
    assert result.compensation_amount == Decimal("0.00")
    assert result.penalty_amount == Decimal("0.00")
    assert result.hours_before_session >= Decimal("24.00")


def test_student_cancel_confirmed_late(factory):
    now = datetime(2026, 11, 2, 10, 0, 0)
    slot_time = now + timedelta(hours=5)
    booking = create_booking(BookingType.PACKAGE, BookingStatus.CONFIRMED, slot_time)

    policy = factory.get_policy(Role.STUDENT)
    result = policy.calculate(booking, now, "Bận đột xuất", None)

    assert result.restore_session is False
    assert result.refund_amount == Decimal("0.00")
    expected_comp = SESSION_FEE * Decimal("0.50")
    assert result.compensation_amount == expected_comp
    assert result.penalty_amount == Decimal("0.00")


def test_student_cancel_trial(factory):
    now = datetime(2026, 11, 2, 10, 0, 0)
    slot_time = now + timedelta(hours=2)
    booking = create_booking(BookingType.TRIAL, BookingStatus.CONFIRMED, slot_time)

    policy = factory.get_policy(Role.STUDENT)
    result = policy.calculate(booking, now, "Không thử nữa", None)

    assert result.restore_session is False
    assert result.refund_amount == Decimal("0.00")
    assert result.compensation_amount == Decimal("0.00")
    assert result.penalty_amount == Decimal("0.00")


def test_pt_cancel_pending(factory):
    now = datetime(2026, 11, 2, 10, 0, 0)
    slot_time = now + timedelta(hours=10)
    booking = create_booking(BookingType.PACKAGE, BookingStatus.PENDING, slot_time)

    policy = factory.get_policy(Role.PT)
    result = policy.calculate(booking, now, "HLV bận", None)

    assert result.restore_session is True
    assert result.refund_amount == SESSION_FEE
    assert result.compensation_amount == Decimal("0.00")
    assert result.penalty_amount == Decimal("0.00")


def test_pt_cancel_confirmed_advance_notice(factory):
    now = datetime(2026, 11, 2, 10, 0, 0)
    slot_time = now + timedelta(hours=48)
    booking = create_booking(BookingType.PACKAGE, BookingStatus.CONFIRMED, slot_time)

    policy = factory.get_policy(Role.PT)
    result = policy.calculate(booking, now, "HLV đi công tác", None)

    assert result.restore_session is True
    assert result.refund_amount == SESSION_FEE
    assert result.compensation_amount == Decimal("0.00")
    assert result.penalty_amount == Decimal("0.00")


def test_pt_cancel_confirmed_late(factory):
    now = datetime(2026, 11, 2, 10, 0, 0)
    slot_time = now + timedelta(hours=4)
    booking = create_booking(BookingType.PACKAGE, BookingStatus.CONFIRMED, slot_time)

    policy = factory.get_policy(Role.PT)
    result = policy.calculate(booking, now, "HLV ốm đột xuất", None)

    assert result.restore_session is True
    assert result.refund_amount == SESSION_FEE
    expected = SESSION_FEE * Decimal("0.20")
    assert result.compensation_amount == expected
    assert result.penalty_amount == expected


def test_admin_cancel_force_majeure(factory):
    now = datetime(2026, 11, 2, 10, 0, 0)
    slot_time = now + timedelta(hours=2)
    booking = create_booking(BookingType.PACKAGE, BookingStatus.CONFIRMED, slot_time)

    policy = factory.get_policy(Role.ADMIN)
    result = policy.calculate(
        booking,
        now,
        "Phòng tập bảo trì khẩn cấp do mất điện",
        "https://cdn.ptconnect.vn/evidence/power_outage.jpg",
    )

    assert result.restore_session is True
    assert result.refund_amount == SESSION_FEE
    assert result.compensation_amount == Decimal("0.00")
    assert result.penalty_amount == Decimal("0.00")
    assert "power_outage.jpg" in (result.explanation or "")


def test_hours_quantization_thresholds(factory):
    """Test quantization: floor(minutes)/60 at boundary points 23.99, 24.00, 24.01."""
    student_policy = factory.get_policy(Role.STUDENT)
    now = datetime(2026, 11, 2, 12, 0, 0)

    # Exactly 24.00 hours = 1440 minutes
    slot_24 = now + timedelta(hours=24)
    b24 = create_booking(BookingType.PACKAGE, BookingStatus.CONFIRMED, slot_24)
    r24 = student_policy.calculate(b24, now, "Exact 24h", None)
    assert r24.hours_before_session == Decimal("24.00")
    assert r24.restore_session is True  # >= 24h qualifies for full refund

    # 23 hours 59 minutes = 1439 minutes -> floor(1439) / 60 = 23.98
    slot_23_59 = now + timedelta(hours=23, minutes=59)
    b23 = create_booking(BookingType.PACKAGE, BookingStatus.CONFIRMED, slot_23_59)
    r23 = student_policy.calculate(b23, now, "Just under 24h", None)
    assert r23.hours_before_session < Decimal("24.00")
    assert r23.restore_session is False  # < 24h late cancellation

    # 24 hours 1 minute = 1441 minutes -> floor(1441) / 60 = 24.01
    slot_24_01 = now + timedelta(hours=24, minutes=1)
    b24_01 = create_booking(BookingType.PACKAGE, BookingStatus.CONFIRMED, slot_24_01)
    r24_01 = student_policy.calculate(b24_01, now, "Just over 24h", None)
    assert r24_01.hours_before_session > Decimal("24.00")
    assert r24_01.restore_session is True
