from decimal import Decimal
from typing import Any

from app.schemas.base import CamelModel, LocalDate, LocalDateTime


class WorkoutResponse(CamelModel):
    id: int
    plan_id: int | None = None
    exercise_name: str
    target_muscle: str | None = None
    sets: int
    reps: int
    weight_kg: Decimal | None = None
    rest_seconds: int
    video_demo_url: str | None = None

    @classmethod
    def from_entity(cls, w: Any) -> "WorkoutResponse | None":
        if w is None:
            return None
        return cls(
            id=w.id,
            plan_id=w.plan_id or (w.plan.id if getattr(w, "plan", None) else None),
            exercise_name=w.exercise_name,
            target_muscle=w.target_muscle,
            sets=w.sets,
            reps=w.reps,
            weight_kg=w.weight_kg,
            rest_seconds=w.rest_seconds,
            video_demo_url=w.video_demo_url,
        )


class WorkoutPlanResponse(CamelModel):
    id: int
    enrollment_id: int | None = None
    pt_id: int | None = None
    pt_name: str | None = None
    student_name: str | None = None
    course_name: str | None = None
    title: str
    goal: str | None = None
    start_date: LocalDate | None = None
    end_date: LocalDate | None = None
    created_at: LocalDateTime | None = None
    workouts: list[WorkoutResponse] = []

    @classmethod
    def from_entity(cls, p: Any) -> "WorkoutPlanResponse | None":
        if p is None:
            return None

        pt_name = None
        if getattr(p, "pt", None) and getattr(p.pt, "pt", None):
            pt_name = p.pt.pt.full_name

        student_name = None
        course_name = None
        if getattr(p, "enrollment", None):
            if getattr(p.enrollment, "student", None):
                student_name = p.enrollment.student.full_name
            if getattr(p.enrollment, "course", None):
                course_name = p.enrollment.course.title

        workouts = []
        if getattr(p, "workouts", None):
            workouts = [WorkoutResponse.from_entity(w) for w in p.workouts if w]

        return cls(
            id=p.id,
            enrollment_id=p.enrollment_id or (p.enrollment.id if getattr(p, "enrollment", None) else None),
            pt_id=p.pt_id or (p.pt.id if getattr(p, "pt", None) else None),
            pt_name=pt_name,
            student_name=student_name,
            course_name=course_name,
            title=p.title,
            goal=p.goal,
            start_date=p.start_date,
            end_date=p.end_date,
            created_at=p.created_at,
            workouts=workouts,
        )
