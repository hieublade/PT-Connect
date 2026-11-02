from decimal import Decimal

import pytest

from app.core.exceptions import InsufficientBalanceException
from app.models.attendance import Attendance
from app.models.availability_slot import AvailabilitySlot
from app.models.booking import Booking
from app.models.enrollment import Enrollment
from app.models.enums import (
    BookingStatus,
    BookingType,
    EnrollmentStatus,
    SlotStatus,
    UserStatus,
    VerificationStatus,
    WalletStatus,
)
from app.models.pt_profile import PTProfile
from app.models.user import PT, Admin, Student
from app.models.wallet import Wallet


def test_user_polymorphic_and_methods():
    student = Student(full_name="Student A", email="s@test.com", password_hash="hash", phone="0901")
    assert student.get_home_page() == "STUDENT_HOME"
    assert student.get_display_role() == "Học viên"
    assert student.status == UserStatus.ACTIVE

    student.suspend()
    assert student.status == UserStatus.SUSPENDED
    student.pending()
    assert student.status == UserStatus.PENDING
    student.activate()
    assert student.status == UserStatus.ACTIVE

    pt = PT(full_name="PT B", email="pt@test.com", password_hash="hash", phone="0902")
    assert pt.get_home_page() == "PT_DASHBOARD"
    assert pt.get_display_role() == "Huấn luyện viên"

    admin = Admin(full_name="Admin C", email="adm@test.com", password_hash="hash", phone="0903")
    assert admin.get_home_page() == "ADMIN_DASHBOARD"
    assert admin.get_display_role() == "Quản trị viên"


def test_pt_profile_approve_reject():
    pt = PT(full_name="PT B", email="pt@test.com", password_hash="hash", phone="0902", status=UserStatus.PENDING)
    profile = PTProfile(
        pt=pt,
        available_locations="District 1",
        verification_status=VerificationStatus.PENDING,
    )

    profile.approve()
    assert profile.verification_status == VerificationStatus.VERIFIED
    assert pt.status == UserStatus.ACTIVE

    profile.reject()
    assert profile.verification_status == VerificationStatus.REJECTED
    assert pt.status == UserStatus.PENDING


def test_wallet_domain_methods():
    wallet = Wallet(balance=Decimal("1000000.00"), locked_balance=Decimal("200000.00"), status=WalletStatus.ACTIVE)

    # Credit
    wallet.credit(Decimal("500000.00"))
    assert wallet.balance == Decimal("1500000.00")

    # Debit valid
    wallet.debit(Decimal("1000000.00"))
    assert wallet.balance == Decimal("500000.00")

    # Debit exceeding available (locked = 200k, balance = 500k, debit 400k -> remaining 100k < 200k)
    with pytest.raises(InsufficientBalanceException) as exc_info:
        wallet.debit(Decimal("400000.00"))
    assert "Số dư khả dụng không đủ" in str(exc_info.value)

    # Debit penalty (allows going below locked or negative)
    wallet.debit_penalty(Decimal("600000.00"))
    assert wallet.balance == Decimal("-100000.00")

    # Frozen wallet check
    wallet.status = WalletStatus.FROZEN
    with pytest.raises(RuntimeError):  # IllegalStateException
        wallet.credit(Decimal("10000.00"))

    # Invalid amount check
    wallet.status = WalletStatus.ACTIVE
    with pytest.raises(ValueError):  # IllegalArgumentException
        wallet.credit(Decimal("0.00"))
    with pytest.raises(ValueError):
        wallet.debit(Decimal("-100.00"))


def test_booking_domain_methods():
    booking = Booking(
        booking_type=BookingType.PACKAGE,
        session_fee=Decimal("300000.00"),
        status=BookingStatus.PENDING,
    )

    booking.confirm()
    assert booking.status == BookingStatus.CONFIRMED

    # Cannot confirm again
    with pytest.raises(RuntimeError):
        booking.confirm()

    booking.complete()
    assert booking.status == BookingStatus.COMPLETED

    # Cannot cancel completed booking
    with pytest.raises(RuntimeError):
        booking.cancel()

    # Cancel a confirmed booking
    b2 = Booking(
        booking_type=BookingType.PACKAGE,
        session_fee=Decimal("300000.00"),
        status=BookingStatus.CONFIRMED,
    )
    b2.cancel()
    assert b2.status == BookingStatus.CANCELLED

    # Cannot cancel twice
    with pytest.raises(RuntimeError):
        b2.cancel()


def test_enrollment_domain_methods():
    enrollment = Enrollment(
        training_location="Cali Cầu Giấy",
        final_price=Decimal("10000000.00"),
        total_sessions=10,
        remaining_sessions=10,
        status=EnrollmentStatus.ACTIVE,
    )

    enrollment.consume_session()
    assert enrollment.remaining_sessions == 9

    enrollment.restore_session()
    assert enrollment.remaining_sessions == 10

    # Cannot restore beyond total
    with pytest.raises(RuntimeError):
        enrollment.restore_session()

    enrollment.complete()
    assert enrollment.status == EnrollmentStatus.COMPLETED

    # Cannot consume from completed
    with pytest.raises(RuntimeError):
        enrollment.consume_session()


def test_slot_domain_methods():
    slot = AvailabilitySlot(status=SlotStatus.AVAILABLE)
    slot.book()
    assert slot.status == SlotStatus.BOOKED
    slot.release()
    assert slot.status == SlotStatus.AVAILABLE


def test_attendance_domain_methods():
    att = Attendance(student_confirmed=False, pt_confirmed=False)
    assert not att.is_fully_confirmed()

    att.student_confirmed = True
    assert not att.is_fully_confirmed()

    att.pt_confirmed = True
    assert att.is_fully_confirmed()
