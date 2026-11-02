from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AttendanceStatus, VerificationMethod

if TYPE_CHECKING:
    from app.models.booking import Booking


class Attendance(Base):
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), unique=True, nullable=False)
    check_in_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    check_out_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    verification_method: Mapped[VerificationMethod] = mapped_column(
        SQLEnum(VerificationMethod, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=VerificationMethod.OTP,
    )
    student_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    pt_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[AttendanceStatus] = mapped_column(
        SQLEnum(AttendanceStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=AttendanceStatus.PRESENT,
    )

    booking: Mapped["Booking"] = relationship("Booking", back_populates="attendance")

    def __init__(self, **kw):
        kw.setdefault("verification_method", VerificationMethod.OTP)
        kw.setdefault("student_confirmed", False)
        kw.setdefault("pt_confirmed", False)
        kw.setdefault("status", AttendanceStatus.PRESENT)
        super().__init__(**kw)

    def is_fully_confirmed(self) -> bool:
        return bool(self.student_confirmed) and bool(self.pt_confirmed)
