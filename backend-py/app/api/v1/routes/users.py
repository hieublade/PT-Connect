from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.responses import ok_response
from app.models.user import User
from app.schemas.requests.auth import UpdateAvatarRequest, UpdateProfileRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    user_dto = service.get_user_by_email(current_user.email)
    return ok_response(
        data=user_dto.model_dump(mode="json", by_alias=True),
        message="Lấy thông tin tài khoản thành công",
    )


@router.put("/profile")
@router.put("/me")
def update_profile(
    request: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    updated = service.update_profile(current_user.email, request)
    return ok_response(
        data=updated.model_dump(mode="json", by_alias=True),
        message="Cập nhật thông tin hồ sơ thành công",
    )


@router.post("/avatar/upload")
@router.post("/me/avatar/upload")
def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    updated = service.upload_avatar(current_user.email, file)
    return ok_response(
        data=updated.model_dump(mode="json", by_alias=True),
        message="Tải ảnh đại diện lên thành công",
    )


@router.put("/avatar")
@router.put("/me/avatar")
def update_avatar(
    request: UpdateAvatarRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    updated = service.update_avatar(current_user.email, request.avatar_url)
    return ok_response(
        data=updated.model_dump(mode="json", by_alias=True),
        message="Cập nhật ảnh đại diện thành công",
    )


@router.get("/{id}")
def get_user_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    user_dto = service.get_user_by_id(id)
    return ok_response(data=user_dto.model_dump(mode="json", by_alias=True))

