from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enums import Role
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_phone(self, phone: str) -> User | None:
        return self.db.query(User).filter(User.phone == phone).first()

    def exists_by_email(self, email: str) -> bool:
        return self.db.query(User.id).filter(User.email == email).first() is not None

    def exists_by_phone(self, phone: str) -> bool:
        return self.db.query(User.id).filter(User.phone == phone).first() is not None

    def get_all(self) -> list[User]:
        return self.db.query(User).all()

    def get_by_role(self, role: Role) -> list[User]:
        return self.db.query(User).filter(User.role == role).all()

    def count_by_role(self, role: Role) -> int:
        return self.db.query(func.count(User.id)).filter(User.role == role).scalar() or 0

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

