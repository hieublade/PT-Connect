from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundException, UnauthorizedException
from app.core.security import jwt_service, password_hasher
from app.models.enums import UserStatus, WalletStatus
from app.models.wallet import Wallet
from app.repositories.user_repo import UserRepository
from app.repositories.wallet_repo import WalletRepository
from app.schemas.requests.auth import LoginRequest, RegisterRequest
from app.schemas.responses.auth import AuthResponse, UserDTO
from app.services.registration.pt_handler import PtRegistrationHandler
from app.services.registration.student_handler import StudentRegistrationHandler


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.wallet_repo = WalletRepository(db)
        self.registration_handlers = [
            StudentRegistrationHandler(),
            PtRegistrationHandler(),
        ]

    def register(self, request: RegisterRequest) -> AuthResponse:
        if self.user_repo.exists_by_email(request.email):
            raise ValueError(f"Email đã được sử dụng: {request.email}")

        if self.user_repo.exists_by_phone(request.phone):
            raise ValueError(f"Số điện thoại đã được sử dụng: {request.phone}")

        handler = next((h for h in self.registration_handlers if h.supports(request.role)), None)
        if not handler:
            raise ValueError("Hệ thống chỉ hỗ trợ đăng ký cho vai trò STUDENT hoặc PT")

        password_hash = password_hasher.hash_password(request.password)

        with self.db.begin_nested():
            saved_user = handler.register(self.db, request, password_hash)

            wallet = Wallet(
                user_id=saved_user.id,
                balance=Decimal("0.00"),
                locked_balance=Decimal("0.00"),
                currency="VND",
                status=WalletStatus.ACTIVE,
            )
            self.db.add(wallet)
            self.db.flush()

        self.db.commit()
        self.db.refresh(saved_user)

        role_str = saved_user.role.value if hasattr(saved_user.role, "value") else str(saved_user.role)
        token = jwt_service.create_token(
            email=saved_user.email,
            role=role_str,
            user_id=saved_user.id,
            full_name=saved_user.full_name,
        )

        return AuthResponse(
            token=token,
            token_type="Bearer",
            user=UserDTO.from_entity(saved_user),
        )

    def login(self, request: LoginRequest) -> AuthResponse:
        user = self.user_repo.get_by_email(request.email)
        if not user:
            raise UnauthorizedException("Email hoặc mật khẩu không chính xác")

        if not password_hasher.verify_password(request.password, user.password_hash):
            raise UnauthorizedException("Email hoặc mật khẩu không chính xác")

        if user.status == UserStatus.SUSPENDED:
            raise UnauthorizedException("Tài khoản của bạn hiện đang bị tạm khóa")

        role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
        token = jwt_service.create_token(
            email=user.email,
            role=role_str,
            user_id=user.id,
            full_name=user.full_name,
        )

        return AuthResponse(
            token=token,
            token_type="Bearer",
            user=UserDTO.from_entity(user),
        )

    def get_me(self, email: str) -> UserDTO:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise ResourceNotFoundException("Không tìm thấy thông tin tài khoản")
        return UserDTO.from_entity(user)
