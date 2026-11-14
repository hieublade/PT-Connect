from pydantic import field_validator

from app.schemas.base import CamelModel, PaymentMethodIn


class PurchaseCourseRequest(CamelModel):
    course_id: int
    training_location: str
    payment_method: PaymentMethodIn = "WALLET"

    @field_validator("course_id")
    @classmethod
    def validate_course_id(cls, v: int) -> int:
        if v is None:
            raise ValueError("Mã khóa học không được để trống")
        return v

    @field_validator("training_location")
    @classmethod
    def validate_location(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Địa điểm tập luyện cố định không được để trống")
        return v.strip()
