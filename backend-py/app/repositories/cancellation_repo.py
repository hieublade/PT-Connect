from sqlalchemy.orm import Session, selectinload

from app.models.cancellation import Cancellation


class CancellationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, cancellation_id: int) -> Cancellation | None:
        return (
            self.db.query(Cancellation)
            .options(selectinload(Cancellation.booking), selectinload(Cancellation.cancelled_by))
            .filter(Cancellation.id == cancellation_id)
            .first()
        )

    def get_by_booking_id(self, booking_id: int) -> Cancellation | None:
        return (
            self.db.query(Cancellation)
            .options(selectinload(Cancellation.booking), selectinload(Cancellation.cancelled_by))
            .filter(Cancellation.booking_id == booking_id)
            .first()
        )

    def save(self, cancellation: Cancellation) -> Cancellation:
        self.db.add(cancellation)
        self.db.flush()
        return cancellation
