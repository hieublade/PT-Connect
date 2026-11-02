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

        b_id = review.booking.id if review.booking else None
        s_id = review.student.id if review.student else None
        s_name = review.student.full_name if review.student else None
        s_avatar = review.student.avatar_url if review.student else None
        p_id = review.pt.id if review.pt else None

        return cls(
            id=review.id,
            booking_id=b_id,
            student_id=s_id,
            student_name=s_name,
            student_avatar_url=s_avatar,
            pt_id=p_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
        )
