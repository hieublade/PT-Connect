from decimal import Decimal
from typing import Any

from pydantic import field_validator, model_validator

from app.models.enums import CourseStatus
from app.schemas.base import CamelModel, Money, SlotDateTime
from app.schemas.certificate import MAX_CERT_URL_LEN, clean_certificate_url


class UpdatePTProfileRequest(CamelModel):
    bio: str | None = None
    experience_years: int | None = None
    available_locations: str
    location_pricing_note: str | None = None
    certificate_url: str | None = None
    certificate_urls: Any | None = None

    @model_validator(mode="after")
    def _normalize_certificate(self) -> "UpdatePTProfileRequest":
        cleaned = clean_certificate_url(self.certificate_url) or clean_certificate_url(self.certificate_urls)
        if cleaned is not None and len(cleaned) > MAX_CERT_URL_LEN:
            raise ValueError("URL chứng chỉ không được vượt quá 500 ký tự")
        self.certificate_url = cleaned
        self.certificate_urls = cleaned
        return self

    @property
    def clean_certificate_url(self) -> str | None:
        return self.certificate_url

    @field_validator("available_locations")
    @classmethod
    def validate_locations(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Địa điểm nhận dạy không được để trống")
        return v.strip()

    @field_validator("experience_years")
    @classmethod
    def validate_exp(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("Số năm kinh nghiệm phải lớn hơn hoặc bằng 0")
        return v


class CreateCourseRequest(CamelModel):
    title: str
    description: str | None = None
    total_sessions: int
    validity_days: int
    base_price: Money

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Tên khóa học không được để trống")
        return v.strip()

    @field_validator("total_sessions")
    @classmethod
    def validate_sessions(cls, v: int) -> int:
        if v is None:
            raise ValueError("Số buổi học không được để trống")
        if v <= 0:
            raise ValueError("Tổng số buổi học phải lớn hơn 0")
        return v

    @field_validator("validity_days")
    @classmethod
    def validate_validity(cls, v: int) -> int:
        if v is None:
            raise ValueError("Thời hạn khóa học không được để trống")
        if v <= 0:
            raise ValueError("Thời hạn sử dụng phải lớn hơn 0 ngày")
        return v

    @field_validator("base_price")
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        if v is None:
            raise ValueError("Giá khóa học không được để trống")
        if v < Decimal(0):
            raise ValueError("Giá khóa học phải lớn hơn hoặc bằng 0")
        return v


class UpdateCourseRequest(CamelModel):
    title: str
    description: str | None = None
    total_sessions: int
    validity_days: int
    base_price: Money
    status: CourseStatus | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Tên khóa học không được để trống")
        return v.strip()

    @field_validator("total_sessions")
    @classmethod
    def validate_sessions(cls, v: int) -> int:
        if v is None:
            raise ValueError("Số buổi học không được để trống")
        if v <= 0:
            raise ValueError("Tổng số buổi học phải lớn hơn 0")
        return v

    @field_validator("validity_days")
    @classmethod
    def validate_validity(cls, v: int) -> int:
        if v is None:
            raise ValueError("Thời hạn khóa học không được để trống")
        if v <= 0:
            raise ValueError("Thời hạn sử dụng phải lớn hơn 0 ngày")
        return v

    @field_validator("base_price")
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        if v is None:
            raise ValueError("Giá khóa học không được để trống")
        if v < Decimal(0):
            raise ValueError("Giá khóa học phải lớn hơn hoặc bằng 0")
        return v


class CreateSlotRequest(CamelModel):
    start_time: SlotDateTime
    end_time: SlotDateTime
