from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.responses import ok_response
from app.services.pt_profile_service import PTProfileService

router = APIRouter(prefix="/pt-profiles", tags=["PT Profiles"])


@router.get("")
def get_public_pt_list(
    name: str | None = Query(None),
    db: Session = Depends(get_db),
):
    service = PTProfileService(db)
    profiles = service.get_public_pt_profiles(name)
    return ok_response(
        data=[p.model_dump(mode="json", by_alias=True) for p in profiles],
        message="Lấy danh sách Huấn luyện viên thành công",
    )


@router.get("/{id}")
def get_public_pt_profile(
    id: int,
    db: Session = Depends(get_db),
):
    service = PTProfileService(db)
    profile = service.get_public_pt_profile_by_id(id)
    return ok_response(
        data=profile.model_dump(mode="json", by_alias=True),
        message="Lấy thông tin Huấn luyện viên thành công",
    )


@router.get("/{id}/courses")
def get_active_courses(
    id: int,
    db: Session = Depends(get_db),
):
    service = PTProfileService(db)
    courses = service.get_active_courses_by_pt_profile_id(id)
    return ok_response(
        data=[c.model_dump(mode="json", by_alias=True) for c in courses],
        message="Lấy danh sách khóa học của Huấn luyện viên thành công",
    )


@router.get("/{id}/slots")
def get_available_slots(
    id: int,
    db: Session = Depends(get_db),
):
    service = PTProfileService(db)
    slots = service.get_available_slots_by_pt_profile_id(id)
    return ok_response(
        data=[s.model_dump(mode="json", by_alias=True) for s in slots],
        message="Lấy danh sách khung giờ rảnh khả dụng thành công",
    )
