from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.workout_plan import WorkoutPlan


class Workout(Base):
    __tablename__ = "workouts"

    plan_id: Mapped[int] = mapped_column(ForeignKey("workout_plans.id"), primary_key=True)
    exercise_order: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    exercise_name: Mapped[str] = mapped_column(String(150), nullable=False)
    target_muscle: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sets: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    reps: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    rest_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    video_demo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    plan: Mapped["WorkoutPlan"] = relationship("WorkoutPlan", back_populates="workouts")

    def __init__(self, **kw):
        passed_id = kw.pop("id", None)
        if passed_id is not None:
            self._temp_id = int(passed_id)
        super().__init__(**kw)

    @property
    def id(self) -> int:
        if hasattr(self, "_temp_id") and self._temp_id is not None:
            return self._temp_id
        return int(self.exercise_order or 0)

    @id.setter
    def id(self, val: int) -> None:
        self._temp_id = int(val)
