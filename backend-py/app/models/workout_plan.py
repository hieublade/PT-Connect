from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, FetchedValue, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.enrollment import Enrollment
    from app.models.pt_profile import PTProfile
    from app.models.workout import Workout


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    enrollment_id: Mapped[int] = mapped_column(ForeignKey("enrollments.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    goal: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())

    enrollment: Mapped["Enrollment"] = relationship("Enrollment", back_populates="workout_plans")
    workouts: Mapped[list["Workout"]] = relationship(
        "Workout",
        back_populates="plan",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kw):
        if "pt" in kw or "pt_id" in kw:
            raise TypeError("WorkoutPlan không lưu PT trực tiếp (BCNF): PT được suy ra từ enrollment.course.pt")
        super().__init__(**kw)

    @property
    def pt(self) -> "PTProfile | None":
        """PT soạn giáo án, suy ra qua Enrollment -> Course (chỉ đọc, chuẩn hóa BCNF)."""
        return self.enrollment.pt if self.enrollment is not None else None

    @property
    def pt_id(self) -> int | None:
        """pt_id suy ra qua Enrollment -> Course (chỉ đọc, chuẩn hóa BCNF)."""
        return self.enrollment.pt_id if self.enrollment is not None else None

    def is_owned_by_pt(self, pt_id: int) -> bool:
        """Đóng gói kiểm tra quyền sở hữu của PT theo nguyên tắc OOP."""
        current_pt_id = self.pt_id
        return current_pt_id is not None and int(current_pt_id) == int(pt_id)
