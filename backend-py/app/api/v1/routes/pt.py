from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.core.responses import created_response, ok_response
from app.models.enums import Role
from app.models.user import User
from app.schemas.requests.pt import (
    CreateCourseRequest,
    CreateSlotRequest,
    UpdateCourseRequest,
    UpdatePTProfileRequest,
)
from app.services.pt_course_service import PTCourseService
from app.services.pt_profile_service import PTProfileService
from app.services.pt_slot_service import PTSlotService

router = APIRouter(prefix="/pt", tags=["PT"])


# -------------------------------------------------------------
# 1. PT Profile
# -------------------------------------------------------------

@router.get("/profile")
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = PTProfileService(db)
    res = service.get_profile(current_user.email)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Lấy hồ sơ Huấn luyện viên thành công",
    )


@router.put("/profile")
def update_profile(
    request: UpdatePTProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = PTProfileService(db)
    res = service.update_profile(current_user.email, request)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Cập nhật hồ sơ Huấn luyện viên thành công",
    )


# -------------------------------------------------------------
# 2. PT Courses
# -------------------------------------------------------------

@router.post("/courses", status_code=201)
def create_course(
    request: CreateCourseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = PTCourseService(db)
    res = service.create_course(current_user.email, request)
    return created_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Tạo khóa học thành công",
        status_code=201,
    )


@router.get("/courses")
def get_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = PTCourseService(db)
    courses = service.get_courses(current_user.email)
    return ok_response(
        data=[c.model_dump(mode="json", by_alias=True) for c in courses],
        message="Lấy danh sách khóa học thành công",
    )


@router.put("/courses/{id}")
def update_course(
    id: int,
    request: UpdateCourseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = PTCourseService(db)
    res = service.update_course(current_user.email, id, request)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Cập nhật khóa học thành công",
    )


@router.delete("/courses/{id}")
def delete_course(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = PTCourseService(db)
    service.delete_course(current_user.email, id)
    return ok_response(data=None, message="Xóa khóa học thành công")


# -------------------------------------------------------------
# 3. PT Availability Slots
# -------------------------------------------------------------

@router.post("/slots", status_code=201)
def create_slot(
    request: CreateSlotRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = PTSlotService(db)
    res = service.create_slot(current_user.email, request)
    return created_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Tạo khung giờ rảnh thành công",
        status_code=201,
    )


@router.get("/slots")
def get_slots(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = PTSlotService(db)
    slots = service.get_slots(current_user.email)
    return ok_response(
        data=[s.model_dump(mode="json", by_alias=True) for s in slots],
        message="Lấy danh sách khung giờ rảnh thành công",
    )


@router.delete("/slots/{id}")
def delete_slot(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = PTSlotService(db)
    service.delete_slot(current_user.email, id)
    return ok_response(data=None, message="Xóa khung giờ rảnh thành công")
