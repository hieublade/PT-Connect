from pydantic import field_validator

from app.schemas.base import CamelModel


class CreateReviewRequest(CamelModel):
    booking_id: int
    rating: int
    comment: str | None = None

    @field_validator("booking_id")
    @classmethod
    def validate_booking_id(cls, v: int) -> int:
        if v is None:
            raise ValueError("Mã ca tập (bookingId) không được để trống")
        return v

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if v is None:
            raise ValueError("Số sao đánh giá không được để trống")
        if v < 1:
            raise ValueError("Đánh giá tối thiểu là 1 sao")
        if v > 5:
            raise ValueError("Đánh giá tối đa là 5 sao")
        return v
