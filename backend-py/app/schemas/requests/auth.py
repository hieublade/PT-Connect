import re

from pydantic import field_validator

from app.models.enums import Role, UserStatus
from app.schemas.base import CamelModel

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class RegisterRequest(CamelModel):
    full_name: str
    email: str
    password: str
    phone: str
    role: Role

    bio: str | None = None
    experience_years: int | None = None
    available_locations: str | None = None
    location_pricing_note: str | None = None
    certificate_urls: str | None = None

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Họ và tên không được để trống")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Email không được để trống")
        if not EMAIL_REGEX.match(v.strip()):
            raise ValueError("Email không đúng định dạng")
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Mật khẩu không được để trống")
        if len(v) < 6:
            raise ValueError("Mật khẩu phải có tối thiểu 6 ký tự")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Số điện thoại không được để trống")
        return v.strip()


class LoginRequest(CamelModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Email không được để trống")
        if not EMAIL_REGEX.match(v.strip()):
            raise ValueError("Email không đúng định dạng")
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Mật khẩu không được để trống")
        return v


class UpdateAvatarRequest(CamelModel):
    avatar_url: str

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("URL ảnh đại diện không được để trống")
        return v.strip()


class UpdateUserStatusRequest(CamelModel):
    status: UserStatus
