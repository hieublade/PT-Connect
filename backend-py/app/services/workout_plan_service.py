from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.clock import today_local
from app.core.exceptions import BadRequestException, ResourceNotFoundException, UnauthorizedException
from app.models.enums import Role
from app.models.workout import Workout
from app.models.workout_plan import WorkoutPlan
from app.repositories.enrollment_repo import EnrollmentRepository
from app.repositories.pt_profile_repo import PTProfileRepository
from app.repositories.user_repo import UserRepository
from app.repositories.workout_plan_repo import WorkoutPlanRepository
from app.repositories.workout_repo import WorkoutRepository
from app.schemas.requests.workout import CreateWorkoutPlanRequest, CreateWorkoutRequest
from app.schemas.responses.workout import WorkoutPlanResponse, WorkoutResponse


class WorkoutPlanService:
    def __init__(self, db: Session):
        self.db = db
        self.plan_repo = WorkoutPlanRepository(db)
        self.workout_repo = WorkoutRepository(db)
        self.enrollment_repo = EnrollmentRepository(db)
        self.pt_repo = PTProfileRepository(db)
        self.user_repo = UserRepository(db)

    def create_plan(self, pt_email: str, request: CreateWorkoutPlanRequest) -> WorkoutPlanResponse:
        pt_profile = self.pt_repo.get_by_email(pt_email)
        if not pt_profile:
            raise UnauthorizedException("Chỉ Huấn luyện viên mới có quyền tạo giáo án")

        enrollment = self.enrollment_repo.get_by_id(request.enrollment_id)
        if not enrollment:
            raise ResourceNotFoundException(f"Không tìm thấy hợp đồng khóa học với ID: {request.enrollment_id}")

        if not enrollment.is_owned_by_pt(pt_profile.id):
            raise UnauthorizedException("Bạn không phải là Huấn luyện viên phụ trách hợp đồng này")

        start = request.start_date if request.start_date is not None else enrollment.start_date
        end = request.end_date if request.end_date is not None else enrollment.end_date

        if start is None:
            start = today_local()
        if end is None:
            end = start + timedelta(weeks=4)

        if start > end:
            raise BadRequestException("Ngày bắt đầu giáo án không thể sau ngày kết thúc")

        plan = WorkoutPlan(
            enrollment_id=enrollment.id,
            title=request.title,
            goal=request.goal,
            start_date=start,
            end_date=end,
        )
        self.plan_repo.save(plan)
        self.db.commit()

        # Reload with relations
        reloaded = self.plan_repo.get_by_id(plan.id)
        return WorkoutPlanResponse.from_entity(reloaded)

    def add_workout(self, pt_email: str, plan_id: int, request: CreateWorkoutRequest) -> WorkoutResponse:
        pt_profile = self.pt_repo.get_by_email(pt_email)
        if not pt_profile:
            raise UnauthorizedException("Chỉ Huấn luyện viên mới có quyền thêm bài tập")

        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise ResourceNotFoundException(f"Không tìm thấy giáo án với ID: {plan_id}")

        if not plan.is_owned_by_pt(pt_profile.id):
            raise UnauthorizedException("Bạn không phải là Huấn luyện viên của giáo án này")

        # Tự động tính exercise_order nếu không truyền vào
        order = request.exercise_order
        if not order or order <= 0:
            order = len(plan.workouts) + 1 if plan.workouts else 1

        workout = Workout(
            plan_id=plan.id,
            exercise_order=order,
            exercise_name=request.exercise_name,
            target_muscle=request.target_muscle,
            sets=request.sets,
            reps=request.reps,
            weight_kg=request.weight_kg,
            rest_seconds=request.rest_seconds,
            video_demo_url=request.video_demo_url,
        )
        self.workout_repo.save(workout)
        self.db.commit()
        self.db.refresh(workout)
        return WorkoutResponse.from_entity(workout)

    def get_plans_by_enrollment(self, user_email: str, enrollment_id: int) -> list[WorkoutPlanResponse]:
        user = self.user_repo.get_by_email(user_email)
        if not user:
            raise UnauthorizedException("Chưa đăng nhập")

        enrollment = self.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment:
            raise ResourceNotFoundException(f"Không tìm thấy hợp đồng khóa học với ID: {enrollment_id}")

        is_student = (enrollment.student_id == user.id)
        is_pt = (enrollment.pt is not None and enrollment.pt.user_id == user.id)
        is_admin = (user.role == Role.ADMIN)

        if not (is_student or is_pt or is_admin):
            raise UnauthorizedException("Bạn không có quyền xem giáo án của hợp đồng này")

        plans = self.plan_repo.find_by_enrollment_id(enrollment_id)
        return [WorkoutPlanResponse.from_entity(p) for p in plans if p]

    def get_plans_by_pt(self, pt_email: str) -> list[WorkoutPlanResponse]:
        pt_profile = self.pt_repo.get_by_email(pt_email)
        if not pt_profile:
            raise UnauthorizedException("Chỉ Huấn luyện viên mới có danh sách giáo án")

        plans = self.plan_repo.find_by_pt_id(pt_profile.id)
        return [WorkoutPlanResponse.from_entity(p) for p in plans if p]

    def delete_plan(self, pt_email: str, plan_id: int) -> None:
        pt_profile = self.pt_repo.get_by_email(pt_email)
        if not pt_profile:
            raise UnauthorizedException("Chỉ Huấn luyện viên mới có quyền xóa giáo án")

        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise ResourceNotFoundException(f"Không tìm thấy giáo án với ID: {plan_id}")

        if not plan.is_owned_by_pt(pt_profile.id):
            raise UnauthorizedException("Bạn không phải là Huấn luyện viên của giáo án này")

        self.workout_repo.delete_by_plan_id(plan_id)
        self.plan_repo.delete(plan)
        self.db.commit()

    def delete_workout(self, pt_email: str, plan_id: int, workout_id: int) -> None:
        pt_profile = self.pt_repo.get_by_email(pt_email)
        if not pt_profile:
            raise UnauthorizedException("Chỉ Huấn luyện viên mới có quyền xóa bài tập")

        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise ResourceNotFoundException(f"Không tìm thấy giáo án với ID: {plan_id}")

        if not plan.is_owned_by_pt(pt_profile.id):
            raise UnauthorizedException("Bạn không phải là Huấn luyện viên của giáo án này")

        workout = self.workout_repo.get_by_id(workout_id)
        if not workout:
            raise ResourceNotFoundException(f"Không tìm thấy bài tập với ID: {workout_id}")

        if workout.plan_id != plan_id:
            raise BadRequestException("Bài tập không thuộc giáo án này")

        self.workout_repo.delete(workout)
        self.db.commit()
