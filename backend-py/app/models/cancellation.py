from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import FetchedValue, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CancellationStatus

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.user import User


class Cancellation(Base):
    __tablename__ = "cancellations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), unique=True, nullable=False)
    cancelled_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    cancelled_by_role: Mapped[str] = mapped_column(String(20), nullable=False, default="STUDENT")
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    cancelled_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())
    hours_before_session: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    refund_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    compensation_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    penalty_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    evidence_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[CancellationStatus] = mapped_column(
        SQLEnum(CancellationStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=CancellationStatus.PROCESSED,
    )

    booking: Mapped["Booking"] = relationship("Booking", back_populates="cancellation")
    cancelled_by: Mapped["User | None"] = relationship("User", foreign_keys=[cancelled_by_id])

    def __init__(self, **kw):
        kw.setdefault("cancelled_by_role", "STUDENT")
        kw.setdefault("refund_amount", Decimal("0.00"))
        kw.setdefault("compensation_amount", Decimal("0.00"))
        kw.setdefault("penalty_amount", Decimal("0.00"))
        kw.setdefault("status", CancellationStatus.PROCESSED)
        super().__init__(**kw)
