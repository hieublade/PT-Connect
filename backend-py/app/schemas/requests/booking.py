from pydantic import field_validator

from app.models.enums import BookingType
from app.schemas.base import CamelModel


class CreateBookingRequest(CamelModel):
    slot_id: int
    booking_type: BookingType = BookingType.PACKAGE
    enrollment_id: int | None = None
    student_note: str | None = None

    @field_validator("slot_id")
    @classmethod
    def validate_slot_id(cls, v: int) -> int:
        if v is None:
            raise ValueError("Mã khung giờ (slotId) không được để trống")
        return v

    @field_validator("student_note")
    @classmethod
    def validate_note(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 255:
            raise ValueError("Ghi chú không được vượt quá 255 ký tự")
        return v


class CancelBookingRequest(CamelModel):
    reason: str | None = None
    evidence_url: str | None = None


class RejectBookingRequest(CamelModel):
    reason: str | None = None
