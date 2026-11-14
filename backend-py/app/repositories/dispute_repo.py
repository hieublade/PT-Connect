from sqlalchemy.orm import Session, selectinload
from app.models.dispute import BookingDispute
from app.models.booking import Booking
from app.models.enums import DisputeStatus
from app.models.availability_slot import AvailabilitySlot
from app.models.pt_profile import PTProfile


class DisputeRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _default_options():
        return (
            selectinload(BookingDispute.sender),
            selectinload(BookingDispute.booking).selectinload(Booking.student),
            selectinload(BookingDispute.booking)
            .selectinload(Booking.slot)
            .selectinload(AvailabilitySlot.pt)
            .selectinload(PTProfile.pt),
            selectinload(BookingDispute.booking).selectinload(Booking.enrollment),
        )

    def get_by_id(self, dispute_id: int) -> BookingDispute | None:
        return (
            self.db.query(BookingDispute)
            .options(*self._default_options())
            .filter(BookingDispute.id == dispute_id)
            .first()
        )

    def get_by_id_with_lock(self, dispute_id: int) -> BookingDispute | None:
        return (
            self.db.query(BookingDispute)
            .options(*self._default_options())
            .filter(BookingDispute.id == dispute_id)
            .with_for_update()
            .first()
        )

    def find_by_booking_id(self, booking_id: int) -> list[BookingDispute]:
        return (
            self.db.query(BookingDispute)
            .options(*self._default_options())
            .filter(BookingDispute.booking_id == booking_id)
            .order_by(BookingDispute.created_at.desc())
            .all()
        )

    def find_all(self, status: DisputeStatus | None = None) -> list[BookingDispute]:
        q = self.db.query(BookingDispute).options(*self._default_options())
        if status:
            q = q.filter(BookingDispute.status == status)
        return q.order_by(BookingDispute.created_at.desc()).all()

    def find_by_user_id(self, user_id: int) -> list[BookingDispute]:
        """Lấy tất cả khiếu nại liên quan đến user (là người gửi hoặc là đối phương)."""
        return (
            self.db.query(BookingDispute)
            .options(*self._default_options())
            .join(Booking, BookingDispute.booking_id == Booking.id)
            .join(AvailabilitySlot, Booking.slot_id == AvailabilitySlot.id)
            .join(PTProfile, AvailabilitySlot.pt_id == PTProfile.id)
            .filter(
                (BookingDispute.sender_id == user_id)
                | (Booking.student_id == user_id)
                | (PTProfile.user_id == user_id)
            )
            .order_by(BookingDispute.created_at.desc())
            .all()
        )

    def create(self, dispute: BookingDispute) -> BookingDispute:
        self.db.add(dispute)
        self.db.flush()
        return dispute

    def update(self, dispute: BookingDispute) -> BookingDispute:
        self.db.flush()
        return dispute

