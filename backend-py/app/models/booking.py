from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    FetchedValue,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    String,
    and_,
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
    from app.models.dispute import BookingDispute
    from app.models.enrollment import Enrollment
    from app.models.pt_profile import PTProfile
    from app.models.review import Review
    from app.models.user import User


class Booking(Base):
    __tablename__ = "bookings"
    # Học viên của ca tập theo gói phải trùng chủ hợp đồng (thay trigger trg_bookings_check_student_integrity).
    # Ca học thử có enrollment_id NULL nên khóa ngoại ghép tự bỏ qua (MATCH SIMPLE).
    __table_args__ = (
        ForeignKeyConstraint(
            ["enrollment_id", "student_id"],
            ["enrollments.id", "enrollments.student_id"],
            name="fk_booking_enroll_student",
        ),
        ForeignKeyConstraint(
            ["pt_id", "slot_start_time"],
            ["availability_slots.pt_id", "availability_slots.start_time"],
            name="fk_booking_slot",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_type: Mapped[BookingType] = mapped_column(
        SQLEnum(BookingType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=BookingType.PACKAGE,
    )
    enrollment_id: Mapped[int | None] = mapped_column(ForeignKey("enrollments.id"), nullable=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    _pt_id: Mapped[int] = mapped_column("pt_id", ForeignKey("pt_profiles.id"), nullable=False)
    slot_start_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now().replace(microsecond=0)
    )
    session_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        SQLEnum(BookingStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=BookingStatus.PENDING,
    )
    student_note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())
    updated_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())

    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])
    slot: Mapped["AvailabilitySlot"] = relationship(
        "AvailabilitySlot",
        back_populates="bookings",
        foreign_keys=[_pt_id, slot_start_time],
        primaryjoin="and_(Booking._pt_id == AvailabilitySlot.pt_id, Booking.slot_start_time == AvailabilitySlot.start_time)",
    )
    # Chỉ join theo enrollment_id; khóa ngoại ghép (enrollment_id, student_id) là ràng buộc toàn vẹn,
    # không phải đường join, nên không để relationship ghi đè student_id.
    enrollment: Mapped["Enrollment | None"] = relationship(
        "Enrollment",
        back_populates="bookings",
        primaryjoin="foreign(Booking.enrollment_id) == Enrollment.id",
    )

    cancellation: Mapped["Cancellation | None"] = relationship(
        "Cancellation", back_populates="booking", uselist=False
    )
    attendance: Mapped["Attendance | None"] = relationship(
        "Attendance", back_populates="booking", uselist=False
    )
    review: Mapped["Review | None"] = relationship(
        "Review", back_populates="booking", uselist=False
    )
    disputes: Mapped[list["BookingDispute"]] = relationship(
        "BookingDispute", back_populates="booking"
    )

    def __init__(self, **kw):
        if "pt" in kw or "pt_id" in kw:
            raise TypeError("Booking không lưu PT trực tiếp (BCNF): PT được suy ra từ slot.pt")
        slot = kw.get("slot")
        if slot is not None:
            if "_pt_id" not in kw and getattr(slot, "pt_id", None) is not None:
                kw["_pt_id"] = slot.pt_id
            if "slot_start_time" not in kw and getattr(slot, "start_time", None) is not None:
                kw["slot_start_time"] = slot.start_time

        passed_slot_id = kw.pop("slot_id", None)
        if passed_slot_id is not None:
            if isinstance(passed_slot_id, int) and passed_slot_id >= 10_000_000_000:
                kw["_pt_id"] = passed_slot_id // 10_000_000_000
                kw["slot_start_time"] = datetime.fromtimestamp(passed_slot_id % 10_000_000_000).replace(microsecond=0)
            else:
                self._temp_slot_id = passed_slot_id
                if "_pt_id" not in kw and isinstance(passed_slot_id, int):
                    kw["_pt_id"] = passed_slot_id

        if "pt_id" in kw:
            kw["_pt_id"] = kw.pop("pt_id")

        kw.setdefault("booking_type", BookingType.PACKAGE)
        kw.setdefault("status", BookingStatus.PENDING)
        kw.setdefault("session_fee", Decimal("0.00"))
        kw.setdefault("_pt_id", 1)
        kw.setdefault("slot_start_time", datetime.now().replace(microsecond=0))
        super().__init__(**kw)

    @property
    def pt_id(self) -> int:
        if self.slot is not None and getattr(self.slot, "pt_id", None) is not None:
            return self.slot.pt_id
        return self._pt_id

    @pt_id.setter
    def pt_id(self, val: object) -> None:
        raise AttributeError("pt_id là thuộc tính chỉ đọc (suy diễn BCNF qua AvailabilitySlot)")

    @property
    def slot_id(self) -> int:
        if hasattr(self, "_temp_slot_id") and self._temp_slot_id is not None:
            return self._temp_slot_id
        if self.slot is not None and hasattr(self.slot, "id"):
            return self.slot.id
        if self._pt_id is not None and self.slot_start_time is not None:
            return int(self._pt_id) * 10_000_000_000 + int(self.slot_start_time.timestamp())
        return 0

    @slot_id.setter
    def slot_id(self, val: int) -> None:
        self._temp_slot_id = val
        if isinstance(val, int) and val >= 10_000_000_000:
            self._pt_id = val // 10_000_000_000
            self.slot_start_time = datetime.fromtimestamp(val % 10_000_000_000).replace(microsecond=0)

    @property
    def pt(self) -> "PTProfile | None":
        """PT của ca tập, suy ra qua AvailabilitySlot (chỉ đọc, chuẩn hóa BCNF)."""
        return self.slot.pt if self.slot is not None else None

    def ensure_consistent_with_enrollment(self) -> None:
        """Bất biến của ca tập theo gói: cùng học viên và cùng PT với hợp đồng.

        Kiểm tra ở tầng domain trước khi DB chặn bằng fk_booking_enroll_student.
        """
        if self.booking_type == BookingType.TRIAL:
            if self.enrollment_id is not None or self.enrollment is not None:
                raise ValueError("Ca học thử (TRIAL) không được gắn với hợp đồng")
            return
        enrollment = self.enrollment
        if enrollment is None:
            raise ValueError("Ca tập theo gói (PACKAGE) bắt buộc phải gắn với hợp đồng")
        if self.student_id is not None and not enrollment.belongs_to_student(self.student_id):
            raise ValueError("Học viên của ca tập không trùng với chủ sở hữu hợp đồng")
        slot_pt_id = self.pt_id
        if slot_pt_id is not None and enrollment.pt_id is not None and slot_pt_id != enrollment.pt_id:
            raise ValueError("Khung giờ đã chọn không thuộc Huấn luyện viên phụ trách hợp đồng")

    def is_owned_by_pt(self, pt_id: int) -> bool:
        """Đóng gói kiểm tra quyền sở hữu của PT theo nguyên tắc OOP."""
        current_pt_id = self.pt_id
        return current_pt_id is not None and int(current_pt_id) == int(pt_id)

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
