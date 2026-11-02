from datetime import date
from decimal import Decimal

from app.models.enums import Role
from app.schemas.requests.auth import RegisterRequest
from app.schemas.requests.enrollment import PurchaseCourseRequest
from app.schemas.requests.pt import CreateCourseRequest
from app.schemas.requests.wallet import TopupRequest
from app.schemas.requests.workout import CreateWorkoutPlanRequest, CreateWorkoutRequest
from app.services.admin_pt_service import AdminPTService
from app.services.admin_statistics_service import AdminStatisticsService
from app.services.auth_service import AuthService
from app.services.enrollment_service import EnrollmentService
from app.services.pt_course_service import PTCourseService
from app.services.wallet_service import WalletService
from app.services.workout_plan_service import WorkoutPlanService


def test_workout_plan_and_admin_statistics(db_session):
    auth_service = AuthService(db_session)
    admin_pt = AdminPTService(db_session)
    course_service = PTCourseService(db_session)
    wallet_service = WalletService(db_session)
    enrollment_service = EnrollmentService(db_session)
    workout_service = WorkoutPlanService(db_session)
    admin_stats_service = AdminStatisticsService(db_session)

    # 1. Register PT & Student
    auth_service.register(
        RegisterRequest(
            full_name="HLV Plan",
            email="hlv_plan@example.com",
            password="Password123!",
            phone="0955555555",
            role=Role.PT,
        )
    )
    pending = admin_pt.get_pending_pts()
    admin_pt.approve_pt(pending[0].id)

    auth_service.register(
        RegisterRequest(
            full_name="Học Viên Plan",
            email="student_plan@example.com",
            password="Password123!",
            phone="0966666666",
            role=Role.STUDENT,
        )
    )

    # 2. Course & Enrollment
    course = course_service.create_course(
        "hlv_plan@example.com",
        CreateCourseRequest(
            title="Khóa Siết Cơ",
            description="Lộ trình",
            total_sessions=8,
            validity_days=30,
            base_price=Decimal("2400000.00"),
        ),
    )
    wallet_service.topup(
        "student_plan@example.com",
        TopupRequest(amount=Decimal("3000000.00"), payment_method="BANK_TRANSFER"),
    )
    enrollment = enrollment_service.purchase_course(
        "student_plan@example.com",
        PurchaseCourseRequest(
            course_id=course.id,
            payment_method="WALLET",
            training_location="Gym Q1",
        ),
    )

    # 3. PT creates Workout Plan
    plan_req = CreateWorkoutPlanRequest(
        enrollment_id=enrollment.id,
        title="Giáo án tháng 11",
        goal="Tăng cơ giảm mỡ",
        start_date=date(2026, 11, 1),
        end_date=date(2026, 11, 30),
    )
    plan = workout_service.create_plan("hlv_plan@example.com", plan_req)
    assert plan.id is not None
    assert plan.title == "Giáo án tháng 11"

    # 4. PT adds workout to plan
    workout_req = CreateWorkoutRequest(
        exercise_name="Barbell Bench Press",
        target_muscle="Ngực",
        sets=4,
        reps=10,
        weight_kg=Decimal("60.00"),
        rest_seconds=90,
    )
    workout = workout_service.add_workout("hlv_plan@example.com", plan.id, workout_req)
    assert workout.id is not None
    assert workout.exercise_name == "Barbell Bench Press"

    # 5. Get plans by enrollment (both student and PT can view)
    plans_student = workout_service.get_plans_by_enrollment("student_plan@example.com", enrollment.id)
    assert len(plans_student) == 1
    assert len(plans_student[0].workouts) == 1

    plans_pt = workout_service.get_plans_by_pt("hlv_plan@example.com")
    assert len(plans_pt) == 1

    # 6. Delete workout
    workout_service.delete_workout("hlv_plan@example.com", plan.id, workout.id)
    plans_after_w_del = workout_service.get_plans_by_enrollment("student_plan@example.com", enrollment.id)
    assert len(plans_after_w_del[0].workouts) == 0

    # 7. Delete plan
    workout_service.delete_plan("hlv_plan@example.com", plan.id)
    plans_after_p_del = workout_service.get_plans_by_pt("hlv_plan@example.com")
    assert len(plans_after_p_del) == 0

    # 8. Admin Statistics
    stats = admin_stats_service.get_statistics()
    assert stats.total_students >= 1
    assert stats.total_pts >= 1
    assert stats.total_revenue == Decimal("2400000.00")

    # 9. Admin Payment Analytics
    payments = admin_stats_service.get_payment_analytics()
    assert len(payments) >= 1
    payments_page = admin_stats_service.get_payment_analytics_page(page=0, size=10)
    assert payments_page.total_elements >= 1
    assert payments_page.number == 0
