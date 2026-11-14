from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.responses import created_response, ok_response
from app.models.user import User
from app.schemas.requests.auth import LoginRequest, RegisterRequest
from app.schemas.responses.auth import UserDTO
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    result = service.register(request)
    # Java returns HTTP 201 with body status 200
    return created_response(
        data=result.model_dump(mode="json", by_alias=True),
        message="Đăng ký tài khoản thành công",
        status_code=201,
        body_status=200,
    )


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    result = service.login(request)
    return ok_response(
        data=result.model_dump(mode="json", by_alias=True),
        message="Đăng nhập thành công",
    )


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    user_dto = UserDTO.from_entity(current_user)
    return ok_response(
        data=user_dto.model_dump(mode="json", by_alias=True) if user_dto else None,
        message="Lấy thông tin tài khoản thành công",
    )
