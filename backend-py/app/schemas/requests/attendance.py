import re

from pydantic import field_validator

from app.schemas.base import CamelModel


class StudentCheckInRequest(CamelModel):
    otp_code: str

    @field_validator("otp_code")
    @classmethod
    def validate_otp(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Mã OTP không được để trống")
        cleaned = v.strip()
        if not re.match(r"^\d{6}$", cleaned):
            raise ValueError("Mã OTP phải gồm đúng 6 chữ số")
        return cleaned
