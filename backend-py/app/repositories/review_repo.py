from sqlalchemy.orm import Session, selectinload

from app.models.booking import Booking
from app.models.pt_profile import PTProfile
from app.models.review import Review


def _with_relations(query):
    # Nạp sẵn booking -> student và booking -> pt -> user để tránh N+1 khi map DTO
    return query.options(
        selectinload(Review.booking).selectinload(Booking.student),
        selectinload(Review.booking).selectinload(Booking.pt).selectinload(PTProfile.pt),
    )


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, review_id: int) -> Review | None:
        return _with_relations(self.db.query(Review)).filter(Review.id == review_id).first()

    def find_by_booking_id(self, booking_id: int) -> Review | None:
        return _with_relations(self.db.query(Review)).filter(Review.booking_id == booking_id).first()

    def exists_by_booking_id(self, booking_id: int) -> bool:
        return self.db.query(Review.id).filter(Review.booking_id == booking_id).first() is not None

    def find_by_pt_id(self, pt_id: int) -> list[Review]:
        # Tương đương JPA findByBookingPtIdOrderByCreatedAtDesc
        return (
            _with_relations(self.db.query(Review))
            .join(Review.booking)
            .filter(Booking.pt_id == pt_id)
            .order_by(Review.created_at.desc(), Review.id.desc())
            .all()
        )

    def find_by_student_id(self, student_id: int) -> list[Review]:
        # Tương đương JPA findByBookingStudentIdOrderByCreatedAtDesc
        return (
            _with_relations(self.db.query(Review))
            .join(Review.booking)
            .filter(Booking.student_id == student_id)
            .order_by(Review.created_at.desc(), Review.id.desc())
            .all()
        )

    def save(self, review: Review) -> Review:
        self.db.add(review)
        self.db.flush()
        return review
