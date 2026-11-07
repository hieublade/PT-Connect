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
    check_in_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
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

    def check_in(
        self,
        now: datetime,
        method: VerificationMethod = VerificationMethod.OTP,
        late: bool = False,
    ) -> None:
        """PT mở phiên điểm danh: ghi giờ check-in, phương thức và trạng thái có mặt / đi muộn."""
        if self.status == AttendanceStatus.ABSENT and self.check_out_time is not None:
            raise RuntimeError("Ca tập đã được ghi nhận vắng mặt, không thể mở lại phiên điểm danh")
        self.check_in_time = now
        self.verification_method = method
        self.status = AttendanceStatus.LATE if late else AttendanceStatus.PRESENT

    def confirm_by_student(self) -> None:
        if self.check_in_time is None:
            raise RuntimeError("Phiên điểm danh chưa được mở, học viên chưa thể xác nhận")
        if self.student_confirmed:
            raise RuntimeError("Học viên đã xác nhận điểm danh cho ca tập này rồi")
        self.student_confirmed = True

    def confirm_by_pt(self) -> None:
        self.pt_confirmed = True

    def check_out(self, now: datetime) -> None:
        """Kết thúc buổi tập. Giờ check-out không được sớm hơn giờ check-in (CHECK chk_attendance_time)."""
        if self.check_in_time is not None and now < self.check_in_time:
            raise RuntimeError("Giờ kết thúc buổi tập không thể trước giờ check-in")
        self.check_out_time = now

    def mark_absent(self, now: datetime) -> None:
        """Học viên vắng mặt: không có sự kiện check-in thực tế nên check_in_time phải là NULL."""
        self.check_in_time = None
        self.student_confirmed = False
        self.pt_confirmed = True
        self.status = AttendanceStatus.ABSENT
        self.check_out_time = now

    @property
    def is_absent(self) -> bool:
        return self.status == AttendanceStatus.ABSENT
