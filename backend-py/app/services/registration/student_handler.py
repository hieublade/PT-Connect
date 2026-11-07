from sqlalchemy.orm import Session

from app.models.enums import Role, UserStatus
from app.models.user import Student, User
from app.schemas.requests.auth import RegisterRequest


class StudentRegistrationHandler:
    def supports(self, role: Role) -> bool:
        return role == Role.STUDENT

    def register(self, db: Session, request: RegisterRequest, password_hash: str) -> User:
        student = Student(
            full_name=request.full_name,
            email=request.email,
            password_hash=password_hash,
            phone=request.phone,
            role=Role.STUDENT,
            status=UserStatus.ACTIVE,
        )
        db.add(student)
        db.flush()
        return student
