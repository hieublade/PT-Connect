from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import DisputeType, DisputeStatus

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.user import User


class BookingDispute(Base):
    """Khiếu nại và trọng tài tranh chấp ca tập / hợp đồng."""

    __tablename__ = "booking_disputes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), unique=True, nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    sender_role: Mapped[str] = mapped_column(String(20), nullable=False, default="STUDENT")
    dispute_type: Mapped[DisputeType] = mapped_column(
        SQLEnum(DisputeType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=DisputeType.WRONG_ABSENT,
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    counter_evidence_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    counter_argument: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[DisputeStatus] = mapped_column(
        SQLEnum(DisputeStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=DisputeStatus.PENDING,
    )
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    deadline_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    booking: Mapped["Booking"] = relationship("Booking", back_populates="disputes")
    sender: Mapped["User"] = relationship("User")

