from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import FetchedValue, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.pt_profile import PTProfile
    from app.models.user import User


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), unique=True, nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    pt_id: Mapped[int] = mapped_column(ForeignKey("pt_profiles.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())

    booking: Mapped["Booking"] = relationship("Booking", back_populates="review")
    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])
    pt: Mapped["PTProfile"] = relationship("PTProfile", foreign_keys=[pt_id])
