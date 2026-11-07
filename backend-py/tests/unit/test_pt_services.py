from datetime import datetime
from decimal import Decimal

from app.models.enums import Role, SlotStatus, VerificationStatus
from app.schemas.requests.auth import RegisterRequest
from app.schemas.requests.pt import CreateCourseRequest, CreateSlotRequest, UpdatePTProfileRequest
from app.services.admin_pt_service import AdminPTService
from app.services.auth_service import AuthService
from app.services.pt_course_service import PTCourseService
from app.services.pt_profile_service import PTProfileService
from app.services.pt_slot_service import PTSlotService


def test_pt_profile_lifecycle_and_admin_approval(db_session):
    auth_service = AuthService(db_session)
    pt_service = PTProfileService(db_session)
    admin_pt = AdminPTService(db_session)

    # 1. Register PT
    reg_req = RegisterRequest(
        full_name="HLV Nam",
        email="nam_pt@example.com",
        password="Password123!",
        phone="0911223344",
        role=Role.PT,
        bio="HLV chuyên nghiệp",
    )
    auth_service.register(reg_req)

    # 2. Check pending list in Admin
    pending = admin_pt.get_pending_pts()
    assert len(pending) == 1
    pt_profile_id = pending[0].id

    # 3. Approve PT
    approved = admin_pt.approve_pt(pt_profile_id)
    assert approved.verification_status == VerificationStatus.VERIFIED

    # 4. PT updates own profile
    update_req = UpdatePTProfileRequest(
        bio="Cập nhật 6 năm kinh nghiệm",
        experience_years=6,
        available_locations="Quận 1, TP HCM",
    )
    updated_profile = pt_service.update_profile("nam_pt@example.com", update_req)
    assert updated_profile.experience_years == 6


def test_pt_course_crud(db_session):
    auth_service = AuthService(db_session)
    admin_pt = AdminPTService(db_session)
    course_service = PTCourseService(db_session)

    # Register & approve PT
    auth_service.register(
        RegisterRequest(
            full_name="HLV Course",
            email="hlv_course@example.com",
            password="Password123!",
            phone="0922334455",
            role=Role.PT,
        )
    )
    pending = admin_pt.get_pending_pts()
    admin_pt.approve_pt(pending[0].id)

    # Create Course
    create_req = CreateCourseRequest(
        title="Khóa Tập Tăng Cơ 12 Buổi",
        description="Lộ trình bài bản",
        total_sessions=12,
        validity_days=30,
        base_price=Decimal("4500000.00"),
    )
    course = course_service.create_course("hlv_course@example.com", create_req)
    assert course.id is not None
    assert course.total_sessions == 12

    # List Courses
    courses = course_service.get_courses("hlv_course@example.com")
    assert len(courses) == 1

    # Delete Course
    course_service.delete_course("hlv_course@example.com", course.id)
    courses_after = course_service.get_courses("hlv_course@example.com")
    assert len(courses_after) == 0


def test_pt_slot_creation_and_deletion(db_session):
    auth_service = AuthService(db_session)
    admin_pt = AdminPTService(db_session)
    slot_service = PTSlotService(db_session)

    # Register & approve PT
    auth_service.register(
        RegisterRequest(
            full_name="HLV Slot",
            email="hlv_slot@example.com",
            password="Password123!",
            phone="0933445566",
            role=Role.PT,
        )
    )
    pending = admin_pt.get_pending_pts()
    admin_pt.approve_pt(pending[0].id)

    # Create Slot
    start = datetime(2026, 12, 1, 9, 0, 0)
    end = datetime(2026, 12, 1, 10, 0, 0)
    slot_req = CreateSlotRequest(
        start_time=start,
        end_time=end,
    )
    slot = slot_service.create_slot("hlv_slot@example.com", slot_req)
    assert slot.id is not None
    assert slot.status == SlotStatus.AVAILABLE

    # List Slots
    slots = slot_service.get_slots("hlv_slot@example.com")
    assert len(slots) == 1

    # Delete Slot
    slot_service.delete_slot("hlv_slot@example.com", slot.id)
    slots_after = slot_service.get_slots("hlv_slot@example.com")
    assert len(slots_after) == 0
