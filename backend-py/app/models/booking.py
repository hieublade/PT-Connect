from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Computed,
    FetchedValue,
    ForeignKey,
    ForeignKeyConstraint,
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
    # Học viên của ca tập theo gói phải trùng chủ hợp đồng (thay trigger trg_bookings_check_student_integrity).
    # Ca học thử có enrollment_id NULL nên khóa ngoại ghép tự bỏ qua (MATCH SIMPLE).
    __table_args__ = (
        ForeignKeyConstraint(
            ["enrollment_id", "student_id"],
            ["enrollments.id", "enrollments.student_id"],
            name="fk_booking_enroll_student",
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
    slot: Mapped["AvailabilitySlot"] = relationship("AvailabilitySlot", back_populates="bookings")
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

    def __init__(self, **kw):
        kw.setdefault("booking_type", BookingType.PACKAGE)
        kw.setdefault("status", BookingStatus.PENDING)
        kw.setdefault("session_fee", Decimal("0.00"))
        if "pt" in kw or "pt_id" in kw:
            raise TypeError("Booking không lưu PT trực tiếp (BCNF): PT được suy ra từ slot.pt")
        super().__init__(**kw)

    @property
    def pt(self) -> "PTProfile | None":
        """PT của ca tập, suy ra qua AvailabilitySlot (chỉ đọc, chuẩn hóa BCNF)."""
        return self.slot.pt if self.slot is not None else None

    @property
    def pt_id(self) -> int | None:
        """pt_id suy ra qua AvailabilitySlot (chỉ đọc, chuẩn hóa BCNF)."""
        return self.slot.pt_id if self.slot is not None else None

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
