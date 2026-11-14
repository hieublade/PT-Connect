from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.workout_plan import WorkoutPlan


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("workout_plans.id"), nullable=False)
    exercise_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    exercise_name: Mapped[str] = mapped_column(String(150), nullable=False)
    target_muscle: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sets: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    reps: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    rest_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    video_demo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    plan: Mapped["WorkoutPlan"] = relationship("WorkoutPlan", back_populates="workouts")
