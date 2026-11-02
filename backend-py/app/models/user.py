from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import FetchedValue, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import Role, UserStatus

if TYPE_CHECKING:
    from app.models.pt_profile import PTProfile
    from app.models.wallet import Wallet


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    role: Mapped[Role] = mapped_column(
        SQLEnum(Role, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=Role.STUDENT,
    )
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserStatus.ACTIVE,
    )
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())
    updated_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())

    wallet: Mapped["Wallet | None"] = relationship("Wallet", back_populates="user", uselist=False)

    __mapper_args__ = {
        "polymorphic_on": role,
    }

    def __init__(self, **kw):
        kw.setdefault("status", UserStatus.ACTIVE)
        super().__init__(**kw)

    def get_home_page(self) -> str:
        return "HOME"

    def get_display_role(self) -> str:
        return "Người dùng"

    def activate(self) -> None:
        self.status = UserStatus.ACTIVE

    def suspend(self) -> None:
        self.status = UserStatus.SUSPENDED

    def pending(self) -> None:
        self.status = UserStatus.PENDING


class Student(User):
    __mapper_args__ = {
        "polymorphic_identity": Role.STUDENT,
    }

    def get_home_page(self) -> str:
        return "STUDENT_HOME"

    def get_display_role(self) -> str:
        return "Học viên"


class PT(User):
    __mapper_args__ = {
        "polymorphic_identity": Role.PT,
    }

    profile: Mapped["PTProfile | None"] = relationship("PTProfile", back_populates="pt", uselist=False)

    def get_home_page(self) -> str:
        return "PT_DASHBOARD"

    def get_display_role(self) -> str:
        return "Huấn luyện viên"


class Admin(User):
    __mapper_args__ = {
        "polymorphic_identity": Role.ADMIN,
    }

    def get_home_page(self) -> str:
        return "ADMIN_DASHBOARD"

    def get_display_role(self) -> str:
        return "Quản trị viên"
