from app.models.review import Review
from app.schemas.base import CamelModel, LocalDateTime


class ReviewResponse(CamelModel):
    id: int
    booking_id: int | None = None
    student_id: int | None = None
    student_name: str | None = None
    student_avatar_url: str | None = None
    pt_id: int | None = None
    rating: int
    comment: str | None = None
    created_at: LocalDateTime | None = None

    @classmethod
    def from_entity(cls, review: Review | None) -> "ReviewResponse | None":
        if review is None:
            return None

        booking = review.booking
        student = booking.student if booking is not None else None
        pt_profile = booking.pt if booking is not None else None

        return cls(
            id=review.id,
            booking_id=booking.id if booking is not None else review.booking_id,
            student_id=student.id if student is not None else (booking.student_id if booking else None),
            student_name=student.full_name if student is not None else None,
            student_avatar_url=student.avatar_url if student is not None else None,
            pt_id=pt_profile.id if pt_profile is not None else (booking.pt_id if booking else None),
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
        )
