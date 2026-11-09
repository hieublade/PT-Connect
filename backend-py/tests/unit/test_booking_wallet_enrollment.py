from datetime import timedelta
from decimal import Decimal

from app.models.enums import AttendanceStatus, BookingStatus, BookingType, Role
from app.schemas.requests.attendance import StudentCheckInRequest
from app.schemas.requests.auth import RegisterRequest
from app.schemas.requests.booking import CreateBookingRequest
from app.schemas.requests.enrollment import PurchaseCourseRequest
from app.schemas.requests.pt import CreateCourseRequest, CreateSlotRequest
from app.schemas.requests.review import CreateReviewRequest
from app.schemas.requests.wallet import TopupRequest, WithdrawRequest
from app.core.exceptions import BadRequestException
from app.services.admin_pt_service import AdminPTService
from app.services.attendance_service import AttendanceService
from app.services.auth_service import AuthService
from app.services.booking_service import BookingService
from app.services.enrollment_service import EnrollmentService
from app.services.pt_course_service import PTCourseService
from app.services.pt_slot_service import PTSlotService
from app.services.review_service import ReviewService
from app.services.wallet_service import WalletService


def test_wallet_enrollment_booking_attendance_review_flow(db_session):
    auth_service = AuthService(db_session)
    admin_pt = AdminPTService(db_session)
    course_service = PTCourseService(db_session)
    slot_service = PTSlotService(db_session)
    wallet_service = WalletService(db_session)
    enrollment_service = EnrollmentService(db_session)
    booking_service = BookingService(db_session)
    attendance_service = AttendanceService(db_session)
    review_service = ReviewService(db_session)

    # 1. Register PT and Student
    auth_service.register(
        RegisterRequest(
            full_name="HLV Fit",
            email="pt_fit@example.com",
            password="Password123!",
            phone="0911111111",
            role=Role.PT,
        )
    )
    pending = admin_pt.get_pending_pts()
    admin_pt.approve_pt(pending[0].id)
    pt_profile_id = pending[0].id

    auth_service.register(
        RegisterRequest(
            full_name="Học Viên Tập",
            email="student_tap@example.com",
            password="Password123!",
            phone="0922222222",
            role=Role.STUDENT,
        )
    )

    # 2. PT creates a Course
    course = course_service.create_course(
        "pt_fit@example.com",
        CreateCourseRequest(
            title="Khóa Giảm Cân Cấp Tốc",
            description="10 buổi",
            total_sessions=10,
            validity_days=30,
            base_price=Decimal("3000000.00"),
        ),
    )

    # 3. Student tops up wallet
    topup_res = wallet_service.topup(
        "student_tap@example.com",
        TopupRequest(
            amount=Decimal("5000000.00"),
            payment_method="BANK_TRANSFER",
        ),
    )
    assert topup_res.amount == Decimal("5000000.00")
    wallet_initial = wallet_service.get_wallet("student_tap@example.com")
    assert wallet_initial.balance == Decimal("5000000.00")

    # 4. Student purchases enrollment
    enrollment = enrollment_service.purchase_course(
        "student_tap@example.com",
        PurchaseCourseRequest(
            course_id=course.id,
            payment_method="WALLET",
            training_location="Phòng Gym ABC, Quận 1",
        ),
    )
    assert enrollment.id is not None
    assert enrollment.remaining_sessions == 10

    # Wallet balance after purchase: 5M - 3M = 2M
    wallet = wallet_service.get_wallet("student_tap@example.com")
    assert wallet.balance == Decimal("2000000.00")

    # 5. PT creates a slot (within 15 minutes of now so attendance can start)
    from app.core.clock import now_local
    start_time = now_local() + timedelta(minutes=5)
    end_time = start_time + timedelta(hours=1)
    slot = slot_service.create_slot(
        "pt_fit@example.com",
        CreateSlotRequest(start_time=start_time, end_time=end_time),
    )

    # 6. Student books slot with PACKAGE
    booking = booking_service.create_booking(
        "student_tap@example.com",
        CreateBookingRequest(
            pt_id=pt_profile_id,
            slot_id=slot.id,
            booking_type=BookingType.PACKAGE,
            enrollment_id=enrollment.id,
            student_note="Tập chân và bụng",
        ),
    )
    assert booking.id is not None
    assert booking.status == BookingStatus.PENDING

    # 7. PT confirms booking
    confirmed_booking = booking_service.confirm_booking("pt_fit@example.com", booking.id)
    assert confirmed_booking.status == BookingStatus.CONFIRMED

    # 8. PT starts attendance session (generates OTP)
    start_att = attendance_service.start_attendance(
        "pt_fit@example.com",
        booking.id,
    )
    otp_code = start_att.otp_code
    assert otp_code is not None
    assert start_att.status == AttendanceStatus.PRESENT

    # 9. Student checks in using OTP
    student_checkin = attendance_service.student_check_in(
        "student_tap@example.com",
        booking.id,
        StudentCheckInRequest(otp_code=otp_code),
    )
    assert student_checkin.student_confirmed is True

    # 10. PT confirms completion
    completed_att = attendance_service.pt_confirm_attendance(
        "pt_fit@example.com",
        booking.id,
    )
    assert completed_att.pt_confirmed is True
    assert completed_att.fully_confirmed is True

    # 11. Student writes review for the completed booking
    review = review_service.create_review(
        "student_tap@example.com",
        CreateReviewRequest(
            booking_id=booking.id,
            rating=5,
            comment="Buổi tập rất nhiệt tình và hiệu quả!",
        ),
    )
    assert review.id is not None
    assert review.rating == 5


def test_pt_wallet_topup_and_withdraw_flow(db_session):
    import pytest
    auth_service = AuthService(db_session)
    wallet_service = WalletService(db_session)

    # 1. Register PT
    auth_service.register(
        RegisterRequest(
            full_name="HLV Ví Điện Tử",
            email="pt_wallet@example.com",
            password="Password123!",
            phone="0933333333",
            role=Role.PT,
        )
    )

    # Check initial wallet balance is 0
    w_initial = wallet_service.get_wallet("pt_wallet@example.com")
    assert w_initial.balance == Decimal("0.00")

    # 2. PT tops up 2,000,000 VND
    topup_res = wallet_service.topup(
        "pt_wallet@example.com",
        TopupRequest(
            amount=Decimal("2000000.00"),
            payment_method="BANK_TRANSFER",
        ),
    )
    assert topup_res.amount == Decimal("2000000.00")
    w_after_topup = wallet_service.get_wallet("pt_wallet@example.com")
    assert w_after_topup.balance == Decimal("2000000.00")

    # 3. PT withdraws 1,200,000 VND
    withdraw_res = wallet_service.withdraw(
        "pt_wallet@example.com",
        WithdrawRequest(
            amount=Decimal("1200000.00"),
            bank_name="Vietcombank",
            account_number="0123456789",
            account_name="HLV VI DIEN TU",
        ),
    )
    assert withdraw_res.amount == Decimal("1200000.00")
    assert "WITHDRAW" in withdraw_res.transaction_ref

    # 4. Check remaining balance: 2M - 1.2M = 800K
    w_after_withdraw = wallet_service.get_wallet("pt_wallet@example.com")
    assert w_after_withdraw.balance == Decimal("800000.00")
    assert len(w_after_withdraw.transactions) == 2

    # 5. Overdraft / Insufficient balance check: withdraw 1,000,000 when only 800,000 available
    with pytest.raises(BadRequestException) as exc_info:
        wallet_service.withdraw(
            "pt_wallet@example.com",
            WithdrawRequest(
                amount=Decimal("1000000.00"),
                bank_name="MBBank",
                account_number="9876543210",
                account_name="HLV VI DIEN TU",
            ),
        )
    assert "không đủ" in str(exc_info.value)

