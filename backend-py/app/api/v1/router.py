from fastapi import APIRouter

from app.api.v1.routes.admin import router as admin_router
from app.api.v1.routes.attendance import router as attendance_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.bookings import router as bookings_router
from app.api.v1.routes.disputes import router as disputes_router
from app.api.v1.routes.enrollments import router as enrollments_router
from app.api.v1.routes.pt import router as pt_router
from app.api.v1.routes.pt_profiles import router as pt_profiles_router
from app.api.v1.routes.public import router as public_router
from app.api.v1.routes.reviews import router as reviews_router
from app.api.v1.routes.student import router as student_router
from app.api.v1.routes.users import router as users_router
from app.api.v1.routes.wallet import router as wallet_router
from app.api.v1.routes.workout_plans import router as workout_plans_router

api_v1_router = APIRouter(prefix="/api/v1")

# Include all route modules
api_v1_router.include_router(public_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(student_router)
api_v1_router.include_router(pt_profiles_router)
api_v1_router.include_router(pt_router)
api_v1_router.include_router(bookings_router)
api_v1_router.include_router(disputes_router)
api_v1_router.include_router(attendance_router)
api_v1_router.include_router(wallet_router)
api_v1_router.include_router(enrollments_router)
api_v1_router.include_router(reviews_router)
api_v1_router.include_router(workout_plans_router)
api_v1_router.include_router(admin_router)
