from sqlalchemy import delete
from sqlalchemy.orm import Session, selectinload

from app.models.workout import Workout


class WorkoutRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, workout_id: int) -> Workout | None:
        return (
            self.db.query(Workout)
            .options(selectinload(Workout.plan))
            .filter(Workout.id == workout_id)
            .first()
        )

    def find_by_plan_id(self, plan_id: int) -> list[Workout]:
        return (
            self.db.query(Workout)
            .options(selectinload(Workout.plan))
            .filter(Workout.plan_id == plan_id)
            .all()
        )

    def save(self, workout: Workout) -> Workout:
        self.db.add(workout)
        self.db.flush()
        return workout

    def delete(self, workout: Workout) -> None:
        self.db.delete(workout)
        self.db.flush()

    def delete_by_plan_id(self, plan_id: int) -> None:
        self.db.execute(delete(Workout).where(Workout.plan_id == plan_id))
        self.db.flush()
