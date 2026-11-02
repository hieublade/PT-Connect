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
    pt_id: Mapped[int] = mapped_column(ForeignKey("pt_profiles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    goal: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())

    enrollment: Mapped["Enrollment"] = relationship("Enrollment", back_populates="workout_plans")
    pt: Mapped["PTProfile"] = relationship("PTProfile", foreign_keys=[pt_id])
    workouts: Mapped[list["Workout"]] = relationship(
        "Workout",
        back_populates="plan",
        cascade="all, delete-orphan",
    )
