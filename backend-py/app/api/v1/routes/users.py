from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.responses import ok_response
from app.models.user import User
from app.schemas.requests.auth import UpdateAvatarRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/{id}")
def get_user_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    user_dto = service.get_user_by_id(id)
    return ok_response(data=user_dto.model_dump(mode="json", by_alias=True))


@router.put("/avatar")
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
