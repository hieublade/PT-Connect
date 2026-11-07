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
    """Bảng reviews theo chuẩn 3NF: chỉ còn booking_id.
    Học viên và PT được suy ra qua booking (booking.student, booking.pt)."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())

    booking: Mapped["Booking"] = relationship("Booking", back_populates="review")

    # ---- Thuộc tính dẫn xuất (read-only), giữ API cũ của model cho code nội bộ ----
    @property
    def student(self) -> "User | None":
        return self.booking.student if self.booking is not None else None

    @property
    def student_id(self) -> int | None:
        return self.booking.student_id if self.booking is not None else None

    @property
    def pt(self) -> "PTProfile | None":
        return self.booking.pt if self.booking is not None else None

    @property
    def pt_id(self) -> int | None:
        return self.booking.pt_id if self.booking is not None else None
