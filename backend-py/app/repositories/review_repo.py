from sqlalchemy.orm import Session, selectinload

from app.models.pt_profile import PTProfile
from app.models.review import Review


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, review_id: int) -> Review | None:
        return (
            self.db.query(Review)
            .options(
                selectinload(Review.booking),
                selectinload(Review.student),
                selectinload(Review.pt).selectinload(PTProfile.pt),
            )
            .filter(Review.id == review_id)
            .first()
        )

    def find_by_booking_id(self, booking_id: int) -> Review | None:
        return (
            self.db.query(Review)
            .options(
                selectinload(Review.booking),
                selectinload(Review.student),
                selectinload(Review.pt).selectinload(PTProfile.pt),
            )
            .filter(Review.booking_id == booking_id)
            .first()
        )

    def find_by_pt_id(self, pt_id: int) -> list[Review]:
        return (
            self.db.query(Review)
            .options(
                selectinload(Review.booking),
                selectinload(Review.student),
                selectinload(Review.pt).selectinload(PTProfile.pt),
            )
            .filter(Review.pt_id == pt_id)
            .order_by(Review.created_at.desc())
            .all()
        )

    def find_by_student_id(self, student_id: int) -> list[Review]:
        return (
            self.db.query(Review)
            .options(
                selectinload(Review.booking),
                selectinload(Review.student),
                selectinload(Review.pt).selectinload(PTProfile.pt),
            )
            .filter(Review.student_id == student_id)
            .order_by(Review.created_at.desc())
            .all()
        )

    def save(self, review: Review) -> Review:
        self.db.add(review)
        self.db.flush()
        return review
