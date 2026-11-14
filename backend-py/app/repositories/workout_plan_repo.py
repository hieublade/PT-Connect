from sqlalchemy.orm import Session, selectinload

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.pt_profile import PTProfile
from app.models.workout_plan import WorkoutPlan


class WorkoutPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _default_options():
        return (
            selectinload(WorkoutPlan.enrollment).selectinload(Enrollment.student),
            selectinload(WorkoutPlan.enrollment).selectinload(Enrollment.course).selectinload(Course.pt).selectinload(PTProfile.pt),
            selectinload(WorkoutPlan.enrollment).selectinload(Enrollment.course).selectinload(Course.pt).selectinload(PTProfile.locations),
            selectinload(WorkoutPlan.workouts),
        )

    def get_by_id(self, plan_id: int) -> WorkoutPlan | None:
        return (
            self.db.query(WorkoutPlan)
            .options(*self._default_options())
            .filter(WorkoutPlan.id == plan_id)
            .first()
        )

    def find_by_enrollment_id(self, enrollment_id: int) -> list[WorkoutPlan]:
        return (
            self.db.query(WorkoutPlan)
            .options(*self._default_options())
            .filter(WorkoutPlan.enrollment_id == enrollment_id)
            .order_by(WorkoutPlan.created_at.desc())
            .all()
        )

    def find_by_pt_id(self, pt_id: int) -> list[WorkoutPlan]:
        return (
            self.db.query(WorkoutPlan)
            .join(WorkoutPlan.enrollment)
            .join(Enrollment.course)
            .options(*self._default_options())
            .filter(Course.pt_id == pt_id)
            .order_by(WorkoutPlan.created_at.desc())
            .all()
        )

    def save(self, plan: WorkoutPlan) -> WorkoutPlan:
        self.db.add(plan)
        self.db.flush()
        return plan

    def delete(self, plan: WorkoutPlan) -> None:
        self.db.delete(plan)
        self.db.flush()
