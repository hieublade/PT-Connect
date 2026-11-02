from sqlalchemy.orm import Session, selectinload

from app.models.enrollment import Enrollment
from app.models.pt_profile import PTProfile
from app.models.workout_plan import WorkoutPlan


class WorkoutPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, plan_id: int) -> WorkoutPlan | None:
        return (
            self.db.query(WorkoutPlan)
            .options(
                selectinload(WorkoutPlan.enrollment).selectinload(Enrollment.student),
                selectinload(WorkoutPlan.enrollment).selectinload(Enrollment.course),
                selectinload(WorkoutPlan.pt).selectinload(PTProfile.pt),
                selectinload(WorkoutPlan.workouts),
            )
            .filter(WorkoutPlan.id == plan_id)
            .first()
        )

    def find_by_enrollment_id(self, enrollment_id: int) -> list[WorkoutPlan]:
        return (
            self.db.query(WorkoutPlan)
            .options(
                selectinload(WorkoutPlan.enrollment).selectinload(Enrollment.student),
                selectinload(WorkoutPlan.enrollment).selectinload(Enrollment.course),
                selectinload(WorkoutPlan.pt).selectinload(PTProfile.pt),
                selectinload(WorkoutPlan.workouts),
            )
            .filter(WorkoutPlan.enrollment_id == enrollment_id)
            .order_by(WorkoutPlan.created_at.desc())
            .all()
        )

    def find_by_pt_id(self, pt_id: int) -> list[WorkoutPlan]:
        return (
            self.db.query(WorkoutPlan)
            .options(
                selectinload(WorkoutPlan.enrollment).selectinload(Enrollment.student),
                selectinload(WorkoutPlan.enrollment).selectinload(Enrollment.course),
                selectinload(WorkoutPlan.pt).selectinload(PTProfile.pt),
                selectinload(WorkoutPlan.workouts),
            )
            .filter(WorkoutPlan.pt_id == pt_id)
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
