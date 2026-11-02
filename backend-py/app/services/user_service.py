from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundException
from app.models.enums import Role, UserStatus
from app.repositories.user_repo import UserRepository
from app.schemas.responses.auth import UserDTO


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_all_users(self) -> list[UserDTO]:
        users = self.user_repo.get_all()
        return [UserDTO.from_entity(u) for u in users]

    def get_users_by_role(self, role: Role) -> list[UserDTO]:
        users = self.user_repo.get_by_role(role)
        return [UserDTO.from_entity(u) for u in users]

    def get_user_by_id(self, user_id: int) -> UserDTO:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundException(f"Không tìm thấy người dùng với ID: {user_id}")
        return UserDTO.from_entity(user)

    def update_avatar(self, email: str, avatar_url: str) -> UserDTO:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise ResourceNotFoundException(f"Không tìm thấy người dùng với email: {email}")

        user.avatar_url = avatar_url
        self.db.commit()
        self.db.refresh(user)
        return UserDTO.from_entity(user)

    def update_user_status(self, user_id: int, status: UserStatus) -> UserDTO:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundException(f"Không tìm thấy người dùng với ID: {user_id}")

        user.status = status
        self.db.commit()
        self.db.refresh(user)
        return UserDTO.from_entity(user)
