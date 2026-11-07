from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, FetchedValue, ForeignKey, Integer, Numeric, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CancellationActorRole, CancellationStatus

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.user import User


class Cancellation(Base):
    """Bản ghi hủy ca tập.

    `cancelled_by_role` là Audit Role Snapshot: SYSTEM thì không có người hủy,
    các vai trò còn lại bắt buộc có `cancelled_by_id` (đồng bộ CHECK `chk_cancel_actor`).
    """

    __tablename__ = "cancellations"
    __table_args__ = (
        CheckConstraint(
            "(cancelled_by_role = 'SYSTEM' AND cancelled_by_id IS NULL) OR "
            "(cancelled_by_role IN ('STUDENT', 'PT', 'ADMIN') AND cancelled_by_id IS NOT NULL)",
            name="chk_cancel_actor",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), unique=True, nullable=False)
    cancelled_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    cancelled_by_role: Mapped[CancellationActorRole] = mapped_column(
        SQLEnum(CancellationActorRole, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=CancellationActorRole.STUDENT,
    )
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    cancelled_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())
    hours_before_session: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    refund_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    compensation_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    penalty_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    evidence_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[CancellationStatus] = mapped_column(
        SQLEnum(CancellationStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=CancellationStatus.PROCESSED,
    )

    booking: Mapped["Booking"] = relationship("Booking", back_populates="cancellation")
    cancelled_by: Mapped["User | None"] = relationship("User", foreign_keys=[cancelled_by_id])

    def __init__(self, **kw: Any):
        role = CancellationActorRole(kw.pop("cancelled_by_role", CancellationActorRole.STUDENT))
        actor = kw.get("cancelled_by")
        actor_id = kw.get("cancelled_by_id")
        self._validate_actor(role, actor_id if actor_id is not None else getattr(actor, "id", None), actor is not None)
        kw["cancelled_by_role"] = role
        kw.setdefault("refund_amount", Decimal("0.00"))
        kw.setdefault("compensation_amount", Decimal("0.00"))
        kw.setdefault("penalty_amount", Decimal("0.00"))
        kw.setdefault("status", CancellationStatus.PROCESSED)
        super().__init__(**kw)

    @staticmethod
    def _validate_actor(role: CancellationActorRole, actor_id: int | None, has_actor: bool) -> None:
        if role.requires_user and actor_id is None and not has_actor:
            raise ValueError(f"Hủy lịch với vai trò {role.value} bắt buộc phải có người hủy (cancelled_by_id)")
        if not role.requires_user and (actor_id is not None or has_actor):
            raise ValueError("Hủy lịch tự động bởi SYSTEM không được gắn với tài khoản người dùng")

    @classmethod
    def by_user(
        cls, booking_id: int, actor: "User", role: CancellationActorRole | str, **details: Any
    ) -> "Cancellation":
        """Tạo bản ghi hủy do một người dùng thực hiện (STUDENT / PT / ADMIN)."""
        role = CancellationActorRole(role)
        if not role.requires_user:
            raise ValueError("Vai trò SYSTEM phải dùng Cancellation.by_system()")
        if actor is None or actor.id is None:
            raise ValueError(f"Hủy lịch với vai trò {role.value} bắt buộc phải có người hủy")
        return cls(booking_id=booking_id, cancelled_by_id=actor.id, cancelled_by_role=role, **details)

    @classmethod
    def by_system(cls, booking_id: int, **details: Any) -> "Cancellation":
        """Tạo bản ghi hủy tự động bởi hệ thống, không gắn với người dùng nào."""
        return cls(booking_id=booking_id, cancelled_by_role=CancellationActorRole.SYSTEM, **details)

    @property
    def is_system_cancellation(self) -> bool:
        return self.cancelled_by_role == CancellationActorRole.SYSTEM

    @property
    def cancelled_by_role_value(self) -> str:
        role = self.cancelled_by_role
        return role.value if isinstance(role, CancellationActorRole) else str(role)
