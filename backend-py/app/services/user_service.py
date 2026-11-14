from pathlib import Path
import uuid
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, ResourceNotFoundException
from app.models.enums import Role, UserStatus
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.requests.auth import UpdateProfileRequest
from app.schemas.responses.auth import UserDTO

AVATAR_UPLOAD_DIR = Path("static/uploads/avatars")
AVATAR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


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

    def get_user_by_email(self, email: str) -> UserDTO:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise ResourceNotFoundException(f"Không tìm thấy người dùng với email: {email}")
        return UserDTO.from_entity(user)

    def update_profile(self, email: str, request: UpdateProfileRequest) -> UserDTO:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise ResourceNotFoundException(f"Không tìm thấy người dùng với email: {email}")

        if request.phone:
            new_phone = request.phone.strip()
            if new_phone != user.phone:
                existing = self.db.query(User).filter(User.phone == new_phone, User.id != user.id).first()
                if existing:
                    raise BadRequestException(f"Số điện thoại này đã được sử dụng bởi tài khoản khác: {new_phone}")
                user.phone = new_phone

        if request.full_name and request.full_name.strip():
            user.full_name = request.full_name.strip()

        if request.avatar_url is not None:
            user.avatar_url = request.avatar_url.strip() if request.avatar_url.strip() else None

        self.db.commit()
        self.db.refresh(user)
        return UserDTO.from_entity(user)

    def upload_avatar(self, email: str, file: UploadFile) -> UserDTO:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise BadRequestException("Chỉ chấp nhận các định dạng tệp hình ảnh (JPEG, PNG, WEBP, GIF)!")

        user = self.user_repo.get_by_email(email)
        if not user:
            raise ResourceNotFoundException(f"Không tìm thấy người dùng với email: {email}")

        ext = Path(file.filename or "avatar.jpg").suffix or ".jpg"
        unique_filename = f"avatar_{user.id}_{uuid.uuid4().hex[:8]}{ext}"
        dest_path = AVATAR_UPLOAD_DIR / unique_filename

        content = file.file.read()
        if len(content) > 5 * 1024 * 1024:
            raise BadRequestException("Dung lượng tập tin ảnh không được vượt quá 5MB!")

        with open(dest_path, "wb") as f:
            f.write(content)

        relative_url = f"/static/uploads/avatars/{unique_filename}"
        user.avatar_url = relative_url
        self.db.commit()
        self.db.refresh(user)
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
