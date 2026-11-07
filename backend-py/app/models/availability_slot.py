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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pt_id: Mapped[int] = mapped_column(ForeignKey("pt_profiles.id"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[SlotStatus] = mapped_column(
        SQLEnum(SlotStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=SlotStatus.AVAILABLE,
    )
    created_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())

    pt: Mapped["PTProfile"] = relationship("PTProfile", back_populates="slots")
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="slot")

    def __init__(self, **kw):
        kw.setdefault("status", SlotStatus.AVAILABLE)
        super().__init__(**kw)

    def book(self) -> None:
        self.status = SlotStatus.BOOKED

    def release(self) -> None:
        self.status = SlotStatus.AVAILABLE
