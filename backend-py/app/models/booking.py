from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Computed,
    FetchedValue,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import BookingStatus, BookingType

if TYPE_CHECKING:
    from app.models.attendance import Attendance
    from app.models.availability_slot import AvailabilitySlot
    from app.models.cancellation import Cancellation
    from app.models.enrollment import Enrollment
    from app.models.pt_profile import PTProfile
    from app.models.review import Review
    from app.models.user import User


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_type: Mapped[BookingType] = mapped_column(
        SQLEnum(BookingType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=BookingType.PACKAGE,
    )
    enrollment_id: Mapped[int | None] = mapped_column(ForeignKey("enrollments.id"), nullable=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    pt_id: Mapped[int] = mapped_column(ForeignKey("pt_profiles.id"), nullable=False)
    slot_id: Mapped[int] = mapped_column(ForeignKey("availability_slots.id"), nullable=False)
    session_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        SQLEnum(BookingStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=BookingStatus.PENDING,
    )
    student_note: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Generated column stored in DB
    active_slot_id: Mapped[int | None] = mapped_column(
        Computed(
            "CASE WHEN status IN ('PENDING', 'CONFIRMED', 'COMPLETED') THEN slot_id ELSE NULL END",
            persisted=True,
        )
    )
    created_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())
    updated_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())

    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])
    pt: Mapped["PTProfile"] = relationship("PTProfile", foreign_keys=[pt_id])
    slot: Mapped["AvailabilitySlot"] = relationship("AvailabilitySlot", back_populates="bookings")
    enrollment: Mapped["Enrollment | None"] = relationship("Enrollment", back_populates="bookings")

    cancellation: Mapped["Cancellation | None"] = relationship(
        "Cancellation", back_populates="booking", uselist=False
    )
    attendance: Mapped["Attendance | None"] = relationship(
        "Attendance", back_populates="booking", uselist=False
    )
    review: Mapped["Review | None"] = relationship(
        "Review", back_populates="booking", uselist=False
    )

    def __init__(self, **kw):
        kw.setdefault("booking_type", BookingType.PACKAGE)
        kw.setdefault("status", BookingStatus.PENDING)
        kw.setdefault("session_fee", Decimal("0.00"))
        super().__init__(**kw)

    def get_training_location(self) -> str | None:
        return self.enrollment.training_location if self.enrollment is not None else None

    def confirm(self) -> None:
        if self.status != BookingStatus.PENDING:
            status_val = self.status.value if hasattr(self.status, "value") else self.status
            raise RuntimeError(
                f"Chỉ có thể xác nhận đơn đặt lịch đang ở trạng thái PENDING. Trạng thái hiện tại: {status_val}"
            )
        self.status = BookingStatus.CONFIRMED

    def cancel(self) -> None:
        if self.status == BookingStatus.CANCELLED:
            raise RuntimeError("Đơn đặt lịch đã ở trạng thái CANCELLED trước đó.")
        if self.status == BookingStatus.COMPLETED:
            raise RuntimeError("Không thể hủy ca tập đã hoàn thành (COMPLETED).")
        self.status = BookingStatus.CANCELLED

    def complete(self) -> None:
        if self.status != BookingStatus.CONFIRMED:
            status_val = self.status.value if hasattr(self.status, "value") else self.status
            raise RuntimeError(
                f"Chỉ có thể hoàn thành ca tập đã được xác nhận (CONFIRMED). Trạng thái hiện tại: {status_val}"
            )
        self.status = BookingStatus.COMPLETED
