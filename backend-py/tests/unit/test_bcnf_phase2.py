"""Kiểm thử chuẩn hóa BCNF đợt 2: ràng buộc DB được phản ánh trong domain model.

Dùng SQLite có bật PRAGMA foreign_keys để khóa ngoại ghép và CHECK được kiểm tra thật.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.db.base import Base
from app.models.attendance import Attendance
from app.models.availability_slot import AvailabilitySlot
from app.models.booking import Booking
from app.models.cancellation import Cancellation
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.enums import (
    AttendanceStatus,
    BookingStatus,
    BookingType,
    CancellationActorRole,
    VerificationMethod,
)
from app.models.pt_location import PTLocation, normalize_location_key
from app.models.pt_profile import PTProfile
from app.models.user import PT, Student
from app.models.workout_plan import WorkoutPlan


@pytest.fixture
def fk_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_fk(dbapi_conn, _record):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def world(fk_session):
    """PT A, PT B, 2 học viên, 1 khóa của PT A, 1 hợp đồng của học viên 1, slot của PT A và PT B."""
    s = fk_session
    pt_user_a = PT(full_name="HLV A", email="a@pt.vn", phone="0900000001", password_hash="x")
    pt_user_b = PT(full_name="HLV B", email="b@pt.vn", phone="0900000002", password_hash="x")
    student_1 = Student(full_name="HV 1", email="s1@hv.vn", phone="0910000001", password_hash="x")
    student_2 = Student(full_name="HV 2", email="s2@hv.vn", phone="0910000002", password_hash="x")
    s.add_all([pt_user_a, pt_user_b, student_1, student_2])
    s.flush()

    profile_a = PTProfile(user_id=pt_user_a.id, available_locations="Phòng Cali Cầu Giấy; FitZone Thanh Xuân")
    profile_b = PTProfile(user_id=pt_user_b.id, available_locations="Studio Đống Đa")
    s.add_all([profile_a, profile_b])
    s.flush()

    course = Course(
        pt_id=profile_a.id, title="Khóa A", total_sessions=10, validity_days=30, base_price=Decimal("3000000")
    )
    s.add(course)
    s.flush()

    enrollment = Enrollment(
        student_id=student_1.id,
        course=course,
        training_location="Phòng Cali Cầu Giấy",
        final_price=Decimal("3000000"),
        total_sessions=10,
        remaining_sessions=10,
        start_date=date(2026, 11, 1),
        end_date=date(2026, 12, 1),
        contract_url="https://example.com/hd.pdf",
    )
    start = datetime(2026, 11, 10, 8, 0)
    slot_a = AvailabilitySlot(pt_id=profile_a.id, start_time=start, end_time=start + timedelta(hours=1))
    slot_a2 = AvailabilitySlot(
        pt_id=profile_a.id, start_time=start + timedelta(hours=2), end_time=start + timedelta(hours=3)
    )
    slot_b = AvailabilitySlot(pt_id=profile_b.id, start_time=start, end_time=start + timedelta(hours=1))
    s.add_all([enrollment, slot_a, slot_a2, slot_b])
    s.commit()
    return {
        "session": s,
        "profile_a": profile_a,
        "profile_b": profile_b,
        "student_1": student_1,
        "student_2": student_2,
        "course": course,
        "enrollment": enrollment,
        "slot_a": slot_a,
        "slot_a2": slot_a2,
        "slot_b": slot_b,
    }


# ---------------------------------------------------------------------------
# 1. pt_locations: cập nhật theo khác biệt + uq_pt_location
# ---------------------------------------------------------------------------


def test_resaving_same_locations_does_not_violate_uq_pt_location(world):
    s, profile = world["session"], world["profile_a"]
    original_ids = sorted(loc.id for loc in profile.locations)

    # PT bấm "Lưu Cập Nhật Hồ Sơ" mà không đổi địa điểm
    profile.replace_locations("Phòng Cali Cầu Giấy; FitZone Thanh Xuân")
    s.commit()

    assert sorted(loc.id for loc in profile.locations) == original_ids
    assert profile.available_locations == "Phòng Cali Cầu Giấy; FitZone Thanh Xuân"


def test_differential_update_keeps_existing_rows_and_adds_removes_only_changes(world):
    s, profile = world["session"], world["profile_a"]
    kept_id = next(loc.id for loc in profile.locations if loc.location_name == "Phòng Cali Cầu Giấy")

    profile.replace_locations("Phòng Cali Cầu Giấy; Nhận dạy tại nhà khu vực Cầu Giấy")
    s.commit()
    s.expire_all()

    rows = s.query(PTLocation).filter_by(pt_id=profile.id).order_by(PTLocation.id).all()
    assert [r.location_name for r in rows] == ["Phòng Cali Cầu Giấy", "Nhận dạy tại nhà khu vực Cầu Giấy"]
    assert rows[0].id == kept_id


def test_accent_and_case_insensitive_duplicates_are_merged(world):
    s, profile = world["session"], world["profile_a"]
    kept_id = next(loc.id for loc in profile.locations if loc.location_name == "Phòng Cali Cầu Giấy")

    profile.add_location("PHONG CALI CAU GIAY")
    assert len(profile.locations) == 2

    # Viết lại không dấu: vẫn là cùng một dòng, chỉ cập nhật tên hiển thị
    profile.replace_locations("Phong  Cali Cau Giay; FitZone Thanh Xuân; fitzone thanh xuan")
    s.commit()
    assert len(profile.locations) == 2
    assert profile.locations[0].id == kept_id
    assert profile.locations[0].location_name == "Phong Cali Cau Giay"
    assert normalize_location_key("Đống Đa") == normalize_location_key("dong da")


def test_db_rejects_duplicate_location_row(world):
    s, profile = world["session"], world["profile_a"]
    s.add(PTLocation(pt_id=profile.id, location_name="FitZone Thanh Xuân"))
    with pytest.raises(IntegrityError):
        s.commit()
    s.rollback()


# ---------------------------------------------------------------------------
# 2. Attendance: domain method, check_in_time NULL khi vắng mặt
# ---------------------------------------------------------------------------


def test_attendance_check_in_and_check_out():
    now = datetime(2026, 11, 10, 8, 20)
    att = Attendance()
    att.check_in(now, VerificationMethod.OTP, late=True)
    assert att.check_in_time == now
    assert att.status == AttendanceStatus.LATE

    with pytest.raises(RuntimeError):
        att.check_out(now - timedelta(minutes=1))
    att.check_out(now + timedelta(hours=1))
    assert att.check_out_time == now + timedelta(hours=1)


def test_mark_absent_clears_check_in_time_even_after_session_opened():
    now = datetime(2026, 11, 10, 8, 0)
    att = Attendance()
    att.check_in(now)  # PT đã mở OTP
    att.mark_absent(now + timedelta(minutes=30))

    assert att.check_in_time is None
    assert att.status == AttendanceStatus.ABSENT
    assert att.pt_confirmed is True and att.student_confirmed is False
    assert att.check_out_time == now + timedelta(minutes=30)
    assert att.is_absent


def test_student_cannot_confirm_before_session_opened():
    with pytest.raises(RuntimeError):
        Attendance().confirm_by_student()


def test_absent_attendance_persists_with_null_check_in(world):
    s = world["session"]
    booking = Booking(
        booking_type=BookingType.TRIAL,
        student_id=world["student_2"].id,
        slot=world["slot_b"],
        status=BookingStatus.CONFIRMED,
    )
    s.add(booking)
    s.flush()
    att = Attendance(booking_id=booking.id)
    att.mark_absent(datetime(2026, 11, 10, 9, 0))
    s.add(att)
    s.commit()

    assert s.get(Attendance, att.id).check_in_time is None


# ---------------------------------------------------------------------------
# 3. Cancellation: CancellationActorRole + chk_cancel_actor
# ---------------------------------------------------------------------------


def _cancel_details():
    return {"reason": "Bận việc", "hours_before_session": Decimal("30.0")}


def test_cancellation_factories_enforce_actor_pairing(world):
    student = world["student_1"]

    by_user = Cancellation.by_user(1, student, "STUDENT", **_cancel_details())
    assert by_user.cancelled_by_id == student.id
    assert by_user.cancelled_by_role is CancellationActorRole.STUDENT
    assert by_user.cancelled_by_role_value == "STUDENT"

    by_system = Cancellation.by_system(2, **_cancel_details())
    assert by_system.cancelled_by_id is None
    assert by_system.is_system_cancellation

    with pytest.raises(ValueError):
        Cancellation.by_user(3, student, CancellationActorRole.SYSTEM, **_cancel_details())
    with pytest.raises(ValueError):
        Cancellation(booking_id=4, cancelled_by_role="PT", **_cancel_details())
    with pytest.raises(ValueError):
        Cancellation(booking_id=5, cancelled_by_id=student.id, cancelled_by_role="SYSTEM", **_cancel_details())
    with pytest.raises(ValueError):
        Cancellation(booking_id=6, cancelled_by_id=student.id, cancelled_by_role="ROBOT", **_cancel_details())


def test_db_check_chk_cancel_actor(world):
    s = world["session"]
    booking = Booking(
        booking_type=BookingType.TRIAL,
        student_id=world["student_2"].id,
        slot=world["slot_b"],
        status=BookingStatus.CANCELLED,
    )
    s.add(booking)
    s.commit()

    # Bỏ qua domain, ghi thẳng SQL để chứng minh CHECK ở tầng DB
    with pytest.raises(IntegrityError):
        s.execute(
            text(
                "INSERT INTO cancellations (booking_id, cancelled_by_id, cancelled_by_role, reason, "
                "hours_before_session, refund_amount, compensation_amount, penalty_amount, status) "
                "VALUES (:b, :u, 'SYSTEM', 'x', 1, 0, 0, 0, 'PROCESSED')"
            ),
            {"b": booking.id, "u": world["student_2"].id},
        )
    s.rollback()

    s.add(Cancellation.by_system(booking.id, **_cancel_details()))
    s.commit()


# ---------------------------------------------------------------------------
# 4. Property pt / pt_id chỉ đọc, suy ra từ slot / course
# ---------------------------------------------------------------------------


def test_derived_pt_properties_are_read_only(world):
    booking = Booking(student_id=world["student_1"].id, slot=world["slot_a"])
    enrollment = world["enrollment"]
    plan = WorkoutPlan(enrollment=enrollment, title="GA", start_date=date(2026, 11, 1), end_date=date(2026, 11, 30))

    assert booking.pt is world["profile_a"] and booking.pt_id == world["profile_a"].id
    assert enrollment.pt is world["profile_a"] and enrollment.pt_id == world["profile_a"].id
    assert plan.pt is world["profile_a"] and plan.pt_id == world["profile_a"].id

    for entity in (booking, enrollment, plan):
        with pytest.raises(AttributeError):
            entity.pt = world["profile_b"]
        with pytest.raises(AttributeError):
            entity.pt_id = world["profile_b"].id

    # Không còn đường nào ghi ngược làm đổi chủ slot / course
    assert world["slot_a"].pt_id == world["profile_a"].id
    assert world["course"].pt_id == world["profile_a"].id


@pytest.mark.parametrize("cls", [Booking, Enrollment, WorkoutPlan])
def test_constructors_reject_direct_pt(cls, world):
    with pytest.raises(TypeError):
        cls(pt=world["profile_a"])
    with pytest.raises(TypeError):
        cls(pt_id=world["profile_a"].id)


# ---------------------------------------------------------------------------
# 5. Booking: uq_enroll_student + fk_booking_enroll_student
# ---------------------------------------------------------------------------


def test_domain_rejects_package_booking_for_other_student(world):
    booking = Booking(
        booking_type=BookingType.PACKAGE,
        student_id=world["student_2"].id,
        slot=world["slot_a"],
        enrollment=world["enrollment"],
    )
    with pytest.raises(ValueError, match="chủ sở hữu hợp đồng"):
        booking.ensure_consistent_with_enrollment()


def test_domain_rejects_slot_of_other_pt(world):
    booking = Booking(
        booking_type=BookingType.PACKAGE,
        student_id=world["student_1"].id,
        slot=world["slot_b"],
        enrollment=world["enrollment"],
    )
    with pytest.raises(ValueError, match="Huấn luyện viên phụ trách"):
        booking.ensure_consistent_with_enrollment()


def test_domain_rejects_trial_with_enrollment(world):
    booking = Booking(
        booking_type=BookingType.TRIAL,
        student_id=world["student_1"].id,
        slot=world["slot_a"],
        enrollment=world["enrollment"],
    )
    with pytest.raises(ValueError):
        booking.ensure_consistent_with_enrollment()


def test_db_composite_fk_blocks_mismatched_student(world):
    s = world["session"]
    # Ghi thẳng cột, bỏ qua domain, để chứng minh khóa ngoại ghép ở tầng DB
    s.add(
        Booking(
            booking_type=BookingType.PACKAGE,
            student_id=world["student_2"].id,
            slot_id=world["slot_a"].id,
            enrollment_id=world["enrollment"].id,
        )
    )
    with pytest.raises(IntegrityError):
        s.commit()
    s.rollback()


def test_db_composite_fk_accepts_owner_and_trial(world):
    s = world["session"]
    package = Booking(
        booking_type=BookingType.PACKAGE,
        student_id=world["student_1"].id,
        slot=world["slot_a"],
        enrollment=world["enrollment"],
    )
    trial = Booking(booking_type=BookingType.TRIAL, student_id=world["student_2"].id, slot=world["slot_a2"])
    package.ensure_consistent_with_enrollment()
    trial.ensure_consistent_with_enrollment()
    s.add_all([package, trial])
    s.commit()

    assert package.student_id == world["enrollment"].student_id
    assert trial.enrollment_id is None


def test_metadata_declares_phase2_constraints():
    names = {
        table: {c.name for c in Base.metadata.tables[table].constraints if c.name}
        for table in ("pt_locations", "enrollments", "bookings", "cancellations")
    }
    assert "uq_pt_location" in names["pt_locations"]
    assert "uq_enroll_student" in names["enrollments"]
    assert "fk_booking_enroll_student" in names["bookings"]
    assert "chk_cancel_actor" in names["cancellations"]
