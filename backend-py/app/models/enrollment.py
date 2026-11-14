from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, FetchedValue, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import EnrollmentStatus

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.course import Course
    from app.models.payment import Payment
    from app.models.pt_profile import PTProfile
    from app.models.user import User
    from app.models.workout_plan import WorkoutPlan


class Enrollment(Base):
    __tablename__ = "enrollments"
    # Đích của khóa ngoại ghép bookings(enrollment_id, student_id) -> enrollments(id, student_id)
    __table_args__ = (UniqueConstraint("id", "student_id", name="uq_enroll_student"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    training_location: Mapped[str] = mapped_column(String(255), nullable=False)
    final_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_sessions: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_sessions: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    contract_url: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[EnrollmentStatus] = mapped_column(
        SQLEnum(EnrollmentStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=EnrollmentStatus.ACTIVE,
    )
    created_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())

    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])
    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="enrollment",
        primaryjoin="Enrollment.id == foreign(Booking.enrollment_id)",
    )
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="enrollment")
    workout_plans: Mapped[list["WorkoutPlan"]] = relationship("WorkoutPlan", back_populates="enrollment")

    def __init__(self, **kw):
        if "pt" in kw or "pt_id" in kw:
            raise TypeError("Enrollment không lưu PT trực tiếp (BCNF): PT được suy ra từ course.pt")
        kw.setdefault("status", EnrollmentStatus.ACTIVE)
        super().__init__(**kw)

    @property
    def pt(self) -> "PTProfile | None":
        """PT phụ trách hợp đồng, suy ra qua Course (chỉ đọc, chuẩn hóa BCNF)."""
        return self.course.pt if self.course is not None else None

    @property
    def pt_id(self) -> int | None:
        """pt_id suy ra qua Course (chỉ đọc, chuẩn hóa BCNF)."""
        return self.course.pt_id if self.course is not None else None

    def belongs_to_student(self, student_id: int) -> bool:
        return self.student_id is not None and int(self.student_id) == int(student_id)

    def is_owned_by_pt(self, pt_id: int) -> bool:
        """Đóng gói kiểm tra quyền sở hữu của PT theo nguyên tắc OOP."""
        current_pt_id = self.pt_id
        return current_pt_id is not None and int(current_pt_id) == int(pt_id)

    def consume_session(self) -> None:
        if self.status != EnrollmentStatus.ACTIVE:
            raise RuntimeError("Hợp đồng không ở trạng thái hoạt động (ACTIVE)")
        if self.remaining_sessions is None or self.remaining_sessions <= 0:
            raise RuntimeError("Hợp đồng đã sử dụng hết số buổi tập khả dụng")
        self.remaining_sessions -= 1

    def restore_session(self) -> None:
        if self.status != EnrollmentStatus.ACTIVE:
            raise RuntimeError("Không thể hoàn buổi cho hợp đồng không ở trạng thái ACTIVE")
        if self.remaining_sessions is not None and self.total_sessions is not None:
            if self.remaining_sessions >= self.total_sessions:
                raise RuntimeError("Số buổi còn lại không thể vượt quá tổng số buổi của hợp đồng")
            self.remaining_sessions += 1

    def complete(self) -> None:
        if self.status != EnrollmentStatus.ACTIVE:
            raise RuntimeError("Chỉ có thể hoàn thành hợp đồng đang ở trạng thái ACTIVE")
        self.status = EnrollmentStatus.COMPLETED
