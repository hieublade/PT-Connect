from datetime import date, datetime, timedelta
from decimal import Decimal
import pytest
from pydantic import ValidationError

from app.core.clock import now_local, today_local
from app.core.exceptions import BadRequestException
from app.models.enums import (
    BookingStatus,
    BookingType,
    DisputeStatus,
    PaymentType,
    Role,
    SlotStatus,
    UserStatus,
    VerificationStatus,
)
from app.models.user import User
from app.schemas.requests.attendance import StudentCheckInRequest
from app.schemas.requests.auth import RegisterRequest, UpdateProfileRequest
from app.schemas.requests.booking import CreateBookingRequest
from app.schemas.requests.dispute import (
    CounterDisputeRequest,
    CreateDisputeRequest,
    RequestEvidenceRequest,
    ResolveDisputeRequest,
    SubmitAdditionalEvidenceRequest,
)
from app.schemas.requests.enrollment import PurchaseCourseRequest
from app.schemas.requests.pt import CreateCourseRequest, CreateSlotRequest
from app.schemas.requests.wallet import TopupRequest, UserWithdrawRequest
from app.schemas.requests.workout import CreateWorkoutPlanRequest
from app.services.admin_pt_service import AdminPTService
from app.services.attendance_service import AttendanceService
from app.services.auth_service import AuthService
from app.services.booking_service import BookingService
from app.services.dispute_service import DisputeService
from app.services.enrollment_service import EnrollmentService
from app.services.pt_course_service import PTCourseService
from app.services.pt_slot_service import PTSlotService
from app.services.user_service import UserService
from app.services.wallet_service import WalletService
from app.services.workout_plan_service import WorkoutPlanService


def test_user_profile_update_and_phone_uniqueness(db_session):
    auth_service = AuthService(db_session)
    user_service = UserService(db_session)

    # Register user 1
    auth_service.register(
        RegisterRequest(
            full_name="Nguyễn Văn A",
            email="nva@example.com",
            password="Password123!",
            phone="0901111111",
            role=Role.STUDENT,
        )
    )
    # Register user 2
    auth_service.register(
        RegisterRequest(
            full_name="Trần Thị B",
            email="ttb@example.com",
            password="Password123!",
            phone="0902222222",
            role=Role.STUDENT,
        )
    )

    # User 1 updates profile
    upd = user_service.update_profile(
        "nva@example.com",
        UpdateProfileRequest(
            full_name="Nguyễn Văn A Cập Nhật",
            phone="0903333333",
            avatar_url="/static/uploads/avatars/test.jpg",
        ),
    )
    assert upd.full_name == "Nguyễn Văn A Cập Nhật"
    assert upd.phone == "0903333333"
    assert upd.avatar_url == "/static/uploads/avatars/test.jpg"

    # User 1 tries to change phone to user 2's phone -> must raise BadRequestException
    with pytest.raises(BadRequestException) as exc:
        user_service.update_profile(
            "nva@example.com",
            UpdateProfileRequest(phone="0902222222"),
        )
    assert "Số điện thoại này đã được sử dụng" in str(exc.value)


def test_wallet_withdrawal_flow(db_session):
    auth_service = AuthService(db_session)
    wallet_service = WalletService(db_session)

    auth_service.register(
        RegisterRequest(
            full_name="Ví Rút Tiền",
            email="wallet_user@example.com",
            password="Password123!",
            phone="0904444444",
            role=Role.STUDENT,
        )
    )

    # Topup 500,000 VND
    wallet_service.topup(
        "wallet_user@example.com",
        TopupRequest(amount=Decimal("500000.00"), payment_method="BANK_TRANSFER"),
    )

    # Withdraw below minimum 50,000 VND -> raises ValidationError from Pydantic validator
    with pytest.raises(ValidationError) as exc1:
        UserWithdrawRequest(
            amount=Decimal("30000.00"),
            bank_name="Vietcombank",
            account_number="123456789",
            account_holder_name="VI RUT TIEN",
        )
    assert "Hạn mức rút tiền tối thiểu là 50,000 VNĐ" in str(exc1.value)

    # Withdraw exceeding available balance -> raises BadRequestException
    with pytest.raises(BadRequestException) as exc2:
        wallet_service.withdraw(
            "wallet_user@example.com",
            UserWithdrawRequest(
                amount=Decimal("600000.00"),
                bank_name="Vietcombank",
                account_number="123456789",
                account_holder_name="VI RUT TIEN",
            ),
        )
    assert "không đủ để rút" in str(exc2.value)

    # Successful withdrawal of 200,000 VND
    res = wallet_service.withdraw(
        "wallet_user@example.com",
        UserWithdrawRequest(
            amount=Decimal("200000.00"),
            bank_name="MBBank",
            account_number="987654321",
            account_holder_name="VI RUT TIEN",
        ),
    )
    assert res.amount == Decimal("200000.00")
    assert res.payment_type == PaymentType.WITHDRAWAL

    wallet = wallet_service.get_wallet("wallet_user@example.com")
    assert wallet.balance == Decimal("300000.00")


def test_session_payout_and_penalty_payment_type(db_session):
    auth_service = AuthService(db_session)
    admin_pt = AdminPTService(db_session)
    course_service = PTCourseService(db_session)
    slot_service = PTSlotService(db_session)
    wallet_service = WalletService(db_session)
    enrollment_service = EnrollmentService(db_session)
    booking_service = BookingService(db_session)
    attendance_service = AttendanceService(db_session)

    # Create Admin
    admin_user = User(
        full_name="Quản Trị Viên",
        email="admin_sys@example.com",
        password_hash="hash",
        phone="0909999999",
        role=Role.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db_session.add(admin_user)
    db_session.commit()

    # Create PT and Student
    auth_service.register(
        RegisterRequest(
            full_name="HLV Payout",
            email="pt_payout@example.com",
            password="Password123!",
            phone="0905555555",
            role=Role.PT,
        )
    )
    pending = admin_pt.get_pending_pts()
    admin_pt.approve_pt(pending[0].id)

    auth_service.register(
        RegisterRequest(
            full_name="Học Viên Payout",
            email="st_payout@example.com",
            password="Password123!",
            phone="0906666666",
            role=Role.STUDENT,
        )
    )

    # PT creates Course (3,000,000 VND for 10 sessions -> 300,000 VND per session)
    course = course_service.create_course(
        "pt_payout@example.com",
        CreateCourseRequest(
            title="Khóa Thể Lực",
            description="Mô tả",
            total_sessions=10,
            validity_days=60,
            base_price=Decimal("3000000.00"),
        ),
    )

    # Student topup & purchase
    wallet_service.topup(
        "st_payout@example.com",
        TopupRequest(amount=Decimal("5000000.00"), payment_method="BANK_TRANSFER"),
    )
    enrollment = enrollment_service.purchase_course(
        "st_payout@example.com",
        PurchaseCourseRequest(course_id=course.id, payment_method="WALLET", training_location="Gym Q1"),
    )

    # PT creates Slot & Student books (start time within 15 minutes to allow attendance check-in)
    slot_start = now_local() + timedelta(minutes=10)
    slot_end = slot_start + timedelta(hours=1)
    slot = slot_service.create_slot(
        "pt_payout@example.com",
        CreateSlotRequest(start_time=slot_start, end_time=slot_end),
    )

    booking = booking_service.create_booking(
        "st_payout@example.com",
        CreateBookingRequest(slot_id=slot.id, enrollment_id=enrollment.id, booking_type=BookingType.PACKAGE),
    )
    booking_service.confirm_booking("pt_payout@example.com", booking.id)

    # Attendance
    att_start = attendance_service.start_attendance("pt_payout@example.com", booking.id)
    attendance_service.student_check_in(
        "st_payout@example.com",
        booking.id,
        StudentCheckInRequest(otp_code=att_start.otp_code),
    )
    attendance_service.pt_confirm_attendance("pt_payout@example.com", booking.id)

    # Verify session payout:
    # Session fee: 300,000 VND. PT gets 90% = 270,000 VND, Admin gets 10% = 30,000 VND.
    pt_wallet = wallet_service.get_wallet("pt_payout@example.com")
    admin_wallet = wallet_service.get_wallet("admin_sys@example.com")

    assert pt_wallet.balance == Decimal("270000.00")
    assert admin_wallet.balance == Decimal("30000.00")

    # Verify penalty payment type is correctly set to PENALTY (ledger fix)
    st_user = auth_service.user_repo.get_by_email("st_payout@example.com")
    penalty_payment, applied = wallet_service.process_booking_penalty(
        st_user.id,
        None,
        Decimal("50000.00"),
    )
    assert penalty_payment is not None
    assert penalty_payment.payment_type == PaymentType.PENALTY
    assert applied == Decimal("50000.00")


def test_dispute_and_contract_termination_flow(db_session):
    auth_service = AuthService(db_session)
    admin_pt = AdminPTService(db_session)
    course_service = PTCourseService(db_session)
    slot_service = PTSlotService(db_session)
    wallet_service = WalletService(db_session)
    enrollment_service = EnrollmentService(db_session)
    booking_service = BookingService(db_session)
    dispute_service = DisputeService(db_session)

    # Register Admin, PT, Student
    admin = User(
        full_name="Admin Dispute",
        email="admin_dsp@example.com",
        password_hash="hash",
        phone="0908888888",
        role=Role.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db_session.add(admin)
    db_session.commit()

    auth_service.register(
        RegisterRequest(
            full_name="HLV Tranh Chấp",
            email="pt_dsp@example.com",
            password="Password123!",
            phone="0907777777",
            role=Role.PT,
        )
    )
    pending = admin_pt.get_pending_pts()
    admin_pt.approve_pt(pending[0].id)

    auth_service.register(
        RegisterRequest(
            full_name="Học Viên Tranh Chấp",
            email="st_dsp@example.com",
            password="Password123!",
            phone="0908888881",
            role=Role.STUDENT,
        )
    )

    # Course (1,000,000 VND for 2 sessions -> 500,000 VND / session)
    course = course_service.create_course(
        "pt_dsp@example.com",
        CreateCourseRequest(
            title="Khóa Đấm Bốc",
            description="Mô tả",
            total_sessions=2,
            validity_days=30,
            base_price=Decimal("1000000.00"),
        ),
    )
    wallet_service.topup(
        "st_dsp@example.com",
        TopupRequest(amount=Decimal("2000000.00"), payment_method="BANK_TRANSFER"),
    )
    enrollment = enrollment_service.purchase_course(
        "st_dsp@example.com",
        PurchaseCourseRequest(course_id=course.id, payment_method="WALLET", training_location="Gym Q1"),
    )

    # Create 2 future slots & bookings
    slot1 = slot_service.create_slot(
        "pt_dsp@example.com",
        CreateSlotRequest(start_time=now_local() + timedelta(hours=1), end_time=now_local() + timedelta(hours=2)),
    )
    slot2 = slot_service.create_slot(
        "pt_dsp@example.com",
        CreateSlotRequest(start_time=now_local() + timedelta(hours=3), end_time=now_local() + timedelta(hours=4)),
    )
    b1 = booking_service.create_booking(
        "st_dsp@example.com",
        CreateBookingRequest(slot_id=slot1.id, enrollment_id=enrollment.id, booking_type=BookingType.PACKAGE),
    )
    b2 = booking_service.create_booking(
        "st_dsp@example.com",
        CreateBookingRequest(slot_id=slot2.id, enrollment_id=enrollment.id, booking_type=BookingType.PACKAGE),
    )

    # Cancel b1 so it qualifies for dispute
    booking_service.cancel_booking_by_student("st_dsp@example.com", b1.id)

    st_user = auth_service.user_repo.get_by_email("st_dsp@example.com")
    pt_user = auth_service.user_repo.get_by_email("pt_dsp@example.com")

    # Student raises dispute
    dsp = dispute_service.create_dispute(
        st_user,
        CreateDisputeRequest(
            booking_id=b1.id,
            dispute_type="CONTRACT_TERMINATION",
            reason="HLV không hỗ trợ đúng cam kết hợp đồng",
        ),
    )
    assert dsp.id is not None
    assert dsp.status == DisputeStatus.PENDING

    # PT submits counter statement
    dsp_counter = dispute_service.submit_counter_argument(
        dsp.id,
        pt_user,
        CounterDisputeRequest(counter_argument="Tôi đã chuẩn bị phòng tập nhưng học viên không đến"),
    )
    assert "Tôi đã chuẩn bị phòng tập" in dsp_counter.counter_argument

    # Admin requests more evidence
    dsp_req = dispute_service.request_more_evidence(
        dsp.id,
        admin,
        RequestEvidenceRequest(admin_notes="Cần cả hai bên gửi lịch sử chat hoặc cuộc gọi"),
    )
    assert dsp_req.status == DisputeStatus.EVIDENCE_REQUESTED

    # Student submits additional evidence
    dsp_add = dispute_service.submit_additional_evidence(
        dsp.id,
        st_user,
        SubmitAdditionalEvidenceRequest(evidence="Đã đính kèm ảnh chụp màn hình cuộc gọi không nhấc máy"),
    )
    assert "Học viên bổ sung" in dsp_add.counter_argument

    # Admin resolves dispute with contract cancellation and refund to student
    dsp_res = dispute_service.resolve_dispute(
        dsp.id,
        admin,
        ResolveDisputeRequest(
            action="CANCEL_CONTRACT_REFUND_STUDENT",
            admin_notes="Chấp thuận hủy hợp đồng và hoàn tiền toàn bộ các buổi chưa học cho học viên",
            force_override=True,
        ),
    )
    assert dsp_res.status == DisputeStatus.RESOLVED_REFUND

    # Verify enrollment is CANCELLED and remaining sessions zeroed out
    enr_check = enrollment_service.enrollment_repo.get_by_id(enrollment.id)
    assert enr_check.status == "CANCELLED"

    # Verify future booking b2 was automatically cancelled and its slot released to AVAILABLE
    b2_check = booking_service.booking_repo.get_by_id(b2.id)
    assert b2_check.status == BookingStatus.CANCELLED

    slot2_check = slot_service.slot_repo.get_by_id(slot2.id)
    assert slot2_check.status == SlotStatus.AVAILABLE


def test_domain_guards(db_session):
    auth_service = AuthService(db_session)
    admin_pt = AdminPTService(db_session)
    slot_service = PTSlotService(db_session)
    booking_service = BookingService(db_session)
    workout_service = WorkoutPlanService(db_session)

    # 1. Register PT & Student
    auth_service.register(
        RegisterRequest(
            full_name="HLV Guard",
            email="pt_guard@example.com",
            password="Password123!",
            phone="0901234567",
            role=Role.PT,
        )
    )
    pending = admin_pt.get_pending_pts()
    admin_pt.approve_pt(pending[0].id)

    auth_service.register(
        RegisterRequest(
            full_name="Học Viên Guard",
            email="st_guard@example.com",
            password="Password123!",
            phone="0907654321",
            role=Role.STUDENT,
        )
    )

    # Guard 1: Cannot create slot with start_time in the past
    with pytest.raises((BadRequestException, ValueError)) as exc1:
        slot_service.create_slot(
            "pt_guard@example.com",
            CreateSlotRequest(
                start_time=now_local() - timedelta(hours=2),
                end_time=now_local() - timedelta(hours=1),
            ),
        )
    assert "quá khứ" in str(exc1.value).lower()

    # Create a valid slot
    slot_valid = slot_service.create_slot(
        "pt_guard@example.com",
        CreateSlotRequest(
            start_time=now_local() + timedelta(hours=2),
            end_time=now_local() + timedelta(hours=3),
        ),
    )

    # Student books trial
    booking_trial = booking_service.create_booking(
        "st_guard@example.com",
        CreateBookingRequest(slot_id=slot_valid.id, booking_type=BookingType.TRIAL),
    )
    assert booking_trial.booking_type == BookingType.TRIAL
    assert booking_trial.session_fee == Decimal("0.00")

    # Guard 2: Cannot book trial a second time with same PT
    slot_valid2 = slot_service.create_slot(
        "pt_guard@example.com",
        CreateSlotRequest(
            start_time=now_local() + timedelta(hours=4),
            end_time=now_local() + timedelta(hours=5),
        ),
    )
    with pytest.raises(BadRequestException) as exc2:
        booking_service.create_booking(
            "st_guard@example.com",
            CreateBookingRequest(slot_id=slot_valid2.id, booking_type=BookingType.TRIAL),
        )
    assert "Mỗi học viên chỉ được học thử 1 lần" in str(exc2.value)
