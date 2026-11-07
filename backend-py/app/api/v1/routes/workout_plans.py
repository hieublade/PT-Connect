from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_roles
from app.core.responses import created_response, ok_response
from app.models.enums import Role
from app.models.user import User
from app.schemas.requests.workout import CreateWorkoutPlanRequest, CreateWorkoutRequest
from app.services.workout_plan_service import WorkoutPlanService

router = APIRouter(tags=["Workout Plans"])


@router.post("/pt/workout-plans", status_code=201)
def create_plan(
    request: CreateWorkoutPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = WorkoutPlanService(db)
    res = service.create_plan(current_user.email, request)
    return created_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Tạo giáo án luyện tập thành công",
        status_code=201,
    )


@router.post("/pt/workout-plans/{id}/workouts", status_code=201)
def add_workout(
    id: int,
    request: CreateWorkoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = WorkoutPlanService(db)
    res = service.add_workout(current_user.email, id, request)
    return created_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Thêm bài tập vào giáo án thành công",
        status_code=201,
    )


@router.get("/enrollments/{id}/workout-plans")
def get_plans_by_enrollment(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WorkoutPlanService(db)
    plans = service.get_plans_by_enrollment(current_user.email, id)
    return ok_response(
        data=[p.model_dump(mode="json", by_alias=True) for p in plans],
        message="Lấy danh sách giáo án của hợp đồng thành công",
    )


@router.get("/pt/workout-plans")
def get_plans_by_pt(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = WorkoutPlanService(db)
    plans = service.get_plans_by_pt(current_user.email)
    return ok_response(
        data=[p.model_dump(mode="json", by_alias=True) for p in plans],
        message="Lấy danh sách giáo án đã tạo thành công",
    )


@router.delete("/pt/workout-plans/{id}")
def delete_plan(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = WorkoutPlanService(db)
    service.delete_plan(current_user.email, id)
    return ok_response(
        data=None,
        message="Xóa giáo án thành công",
    )


@router.delete("/pt/workout-plans/{plan_id}/workouts/{workout_id}")
def delete_workout(
    plan_id: int,
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = WorkoutPlanService(db)
    service.delete_workout(current_user.email, plan_id, workout_id)
    return ok_response(
        data=None,
        message="Xóa bài tập khỏi giáo án thành công",
    )
