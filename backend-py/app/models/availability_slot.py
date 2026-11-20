from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, FetchedValue, ForeignKey, Integer
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import SlotStatus

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.pt_profile import PTProfile


class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"

    pt_id: Mapped[int] = mapped_column(ForeignKey("pt_profiles.id"), primary_key=True)
    start_time: Mapped[datetime] = mapped_column(
        DateTime, primary_key=True, default=datetime.now
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    status: Mapped[SlotStatus] = mapped_column(
        SQLEnum(SlotStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=SlotStatus.AVAILABLE,
    )
    created_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())

    pt: Mapped["PTProfile"] = relationship("PTProfile", back_populates="slots")
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="slot",
        foreign_keys="[Booking._pt_id, Booking.slot_start_time]",
        primaryjoin="and_(AvailabilitySlot.pt_id == Booking._pt_id, AvailabilitySlot.start_time == Booking.slot_start_time)",
    )

    def __init__(self, **kw):
        # Capture and store legacy/test 'id' gracefully if passed
        passed_id = kw.pop("id", None)
        if passed_id is not None:
            self._temp_id = int(passed_id)
        if "start_time" in kw and isinstance(kw["start_time"], datetime):
            kw["start_time"] = kw["start_time"].replace(microsecond=0)
        if "end_time" in kw and isinstance(kw["end_time"], datetime):
            kw["end_time"] = kw["end_time"].replace(microsecond=0)
        kw.setdefault("status", SlotStatus.AVAILABLE)
        super().__init__(**kw)

    @property
    def id(self) -> int:
        """Surrogate identifier property for backwards compatibility with tests and APIs."""
        if hasattr(self, "_temp_id") and self._temp_id is not None:
            return self._temp_id
        if self.pt_id is not None and self.start_time is not None:
            return int(self.pt_id) * 10_000_000_000 + int(self.start_time.timestamp())
        return int(self.pt_id or 0)

    @id.setter
    def id(self, val: int) -> None:
        self._temp_id = int(val)

    def book(self) -> None:
        self.status = SlotStatus.BOOKED

    def release(self) -> None:
        self.status = SlotStatus.AVAILABLE
