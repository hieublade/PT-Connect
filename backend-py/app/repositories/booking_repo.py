from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models.availability_slot import AvailabilitySlot
from app.models.booking import Booking
from app.models.cancellation import Cancellation
from app.models.enums import BookingStatus
from app.models.pt_profile import PTProfile


class BookingRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _default_options():
        return (
            selectinload(Booking.student),
            selectinload(Booking.slot).selectinload(AvailabilitySlot.pt).selectinload(PTProfile.pt),
            selectinload(Booking.slot).selectinload(AvailabilitySlot.pt).selectinload(PTProfile.locations),
            selectinload(Booking.enrollment),
            selectinload(Booking.cancellation),
            selectinload(Booking.attendance),
            selectinload(Booking.review),
        )

    def get_by_id(self, booking_id: int) -> Booking | None:
        return (
            self.db.query(Booking)
            .options(*self._default_options())
            .filter(Booking.id == booking_id)
            .first()
        )

    def get_by_id_with_lock(self, booking_id: int) -> Booking | None:
        return (
            self.db.query(Booking)
            .options(*self._default_options())
            .filter(Booking.id == booking_id)
            .with_for_update()
            .first()
        )

    def find_by_slot_id(self, slot_id: int) -> Booking | None:
        return self.db.query(Booking).filter(Booking.slot_id == slot_id).first()

    def find_by_student_id(self, student_id: int, status: BookingStatus | None = None) -> list[Booking]:
        query = (
            self.db.query(Booking)
            .options(*self._default_options())
            .filter(Booking.student_id == student_id)
        )
        if status is not None:
            query = query.filter(Booking.status == status)
        return query.order_by(Booking.created_at.desc()).all()

    def find_by_pt_id(self, pt_id: int, status: BookingStatus | None = None) -> list[Booking]:
        query = (
            self.db.query(Booking)
            .join(Booking.slot)
            .options(*self._default_options())
            .filter(AvailabilitySlot.pt_id == pt_id)
        )
        if status is not None:
            query = query.filter(Booking.status == status)
        return query.order_by(Booking.created_at.desc()).all()

    def exists_trial_by_student_and_pt(self, student_id: int, pt_id: int) -> bool:
        return (
            self.db.query(Booking.id)
            .join(Booking.slot)
            .filter(
                Booking.student_id == student_id,
                AvailabilitySlot.pt_id == pt_id,
                Booking.booking_type == "TRIAL",
            )
            .first()
            is not None
        )

    def exists_overlapping_booking_for_student(
        self, student_id: int, start_time: datetime, end_time: datetime
    ) -> bool:
        # Check active bookings (not CANCELLED)
        return (
            self.db.query(Booking.id)
            .join(Booking.slot)
            .filter(
                Booking.student_id == student_id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.COMPLETED]),
                AvailabilitySlot.start_time < end_time,
                AvailabilitySlot.end_time > start_time,
            )
            .first()
            is not None
        )

    def count_open_bookings_for_enrollment(self, enrollment_id: int, exclude_booking_id: int | None = None) -> int:
        query = self.db.query(func.count(Booking.id)).filter(
            Booking.enrollment_id == enrollment_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
        )
        if exclude_booking_id is not None:
            query = query.filter(Booking.id != exclude_booking_id)
        return query.scalar() or 0

    def find_all(self, status: BookingStatus | None = None) -> list[Booking]:
        query = self.db.query(Booking).options(*self._default_options())
        if status is not None:
            query = query.filter(Booking.status == status)
        return query.order_by(Booking.created_at.desc()).all()

    def count(self) -> int:
        return self.db.query(func.count(Booking.id)).scalar() or 0

    def find_bookings_with_cancellation(self) -> list[tuple[Booking, Cancellation | None]]:
        return (
            self.db.query(Booking, Cancellation)
            .outerjoin(Cancellation, Cancellation.booking_id == Booking.id)
            .options(
                selectinload(Booking.student),
                selectinload(Booking.slot).selectinload(AvailabilitySlot.pt).selectinload(PTProfile.pt),
                selectinload(Booking.slot),
            )
            .order_by(Booking.created_at.desc())
            .all()
        )

    def find_bookings_with_cancellation_page(
        self, page: int = 0, size: int = 20
    ) -> tuple[list[tuple[Booking, Cancellation | None]], int]:
        total = self.count()
        offset = page * size
        items = (
            self.db.query(Booking, Cancellation)
            .outerjoin(Cancellation, Cancellation.booking_id == Booking.id)
            .options(
                selectinload(Booking.student),
                selectinload(Booking.slot).selectinload(AvailabilitySlot.pt).selectinload(PTProfile.pt),
                selectinload(Booking.slot),
            )
            .order_by(Booking.created_at.desc())
            .offset(offset)
            .limit(size)
            .all()
        )
        return items, total

    def save(self, booking: Booking) -> Booking:
        self.db.add(booking)
        self.db.flush()
        return booking
