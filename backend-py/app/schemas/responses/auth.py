
from app.models.enums import Role, UserStatus
from app.models.user import User
from app.schemas.base import CamelModel, LocalDateTime


class UserDTO(CamelModel):
    id: int
    full_name: str
    email: str
    phone: str
    role: Role
    status: UserStatus
    avatar_url: str | None = None
    created_at: LocalDateTime | None = None
    updated_at: LocalDateTime | None = None
    display_role: str | None = None
    home_page: str | None = None

    @classmethod
    def from_entity(cls, user: User | None) -> "UserDTO | None":
        if user is None:
            return None
        return cls(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            role=user.role,
            status=user.status,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
            updated_at=user.updated_at,
            display_role=user.get_display_role(),
            home_page=user.get_home_page(),
        )


class AuthResponse(CamelModel):
    token: str
    token_type: str = "Bearer"
    user: UserDTO | None = None
