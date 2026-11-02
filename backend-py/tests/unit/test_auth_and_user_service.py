import pytest

from app.core.exceptions import UnauthorizedException
from app.models.enums import Role, UserStatus
from app.schemas.requests.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService
from app.services.user_service import UserService


def test_register_student_and_login(db_session):
    auth_service = AuthService(db_session)

    # Register student
    reg_req = RegisterRequest(
        full_name="Nguyễn Văn A",
        email="student_a@example.com",
        password="Password123!",
        phone="0912345678",
        role=Role.STUDENT,
    )
    auth_res = auth_service.register(reg_req)
    assert auth_res.user.id is not None
    assert auth_res.user.role == Role.STUDENT
    assert auth_res.user.status == UserStatus.ACTIVE

    # Login student
    login_req = LoginRequest(email="student_a@example.com", password="Password123!")
    login_res = auth_service.login(login_req)
    assert login_res.token is not None
    assert login_res.token_type == "Bearer"
    assert login_res.user.email == "student_a@example.com"


def test_register_duplicate_email_raises(db_session):
    auth_service = AuthService(db_session)
    reg_req = RegisterRequest(
        full_name="Nguyễn Văn A",
        email="dup@example.com",
        password="Password123!",
        phone="0912345678",
        role=Role.STUDENT,
    )
    auth_service.register(reg_req)

    with pytest.raises(ValueError, match="Email đã được sử dụng"):
        auth_service.register(reg_req)


def test_register_pt_creates_pending_profile(db_session):
    auth_service = AuthService(db_session)
    reg_req = RegisterRequest(
        full_name="Huấn Luyện Viên X",
        email="pt_x@example.com",
        password="Password123!",
        phone="0987654321",
        role=Role.PT,
        bio="5 năm kinh nghiệm gym",
        experience_years=5,
        available_locations="Hà Nội, Cầu Giấy",
    )
    auth_res = auth_service.register(reg_req)
    assert auth_res.user.role == Role.PT
    assert auth_res.user.status == UserStatus.PENDING


def test_login_wrong_password_raises(db_session):
    auth_service = AuthService(db_session)
    reg_req = RegisterRequest(
        full_name="User Test",
        email="test_wrong_pw@example.com",
        password="Password123!",
        phone="0933333333",
        role=Role.STUDENT,
    )
    auth_service.register(reg_req)

    login_req = LoginRequest(email="test_wrong_pw@example.com", password="WrongPassword!")
    with pytest.raises(UnauthorizedException, match="Email hoặc mật khẩu không chính xác"):
        auth_service.login(login_req)


def test_user_service_avatar_and_status(db_session):
    auth_service = AuthService(db_session)
    user_service = UserService(db_session)

    reg_req = RegisterRequest(
        full_name="User Status",
        email="status_user@example.com",
        password="Password123!",
        phone="0944444444",
        role=Role.STUDENT,
    )
    auth_res = auth_service.register(reg_req)
    user_id = auth_res.user.id

    # Update avatar
    updated = user_service.update_avatar("status_user@example.com", "https://avatar.url/img.png")
    assert updated.avatar_url == "https://avatar.url/img.png"

    # Update status to SUSPENDED
    updated_status = user_service.update_user_status(user_id, UserStatus.SUSPENDED)
    assert updated_status.status == UserStatus.SUSPENDED
