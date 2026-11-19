from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import FetchedValue, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CancellationActorRole, CancellationStatus

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.user import User


class Cancellation(Base):
    """Bản ghi hủy ca tập (Chuẩn BCNF).

    Bảng cơ sở chỉ lưu các thuộc tính nguyên thủy độc lập.
    Các thuộc tính dẫn xuất (hours_before_session, refund_amount, penalty_amount,...)
    và vai trò người hủy (cancelled_by_role suy ra từ cancelled_by_id) được truy xuất động.
    """

    __tablename__ = "cancellations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), unique=True, nullable=False)
    cancelled_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    evidence_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[CancellationStatus] = mapped_column(
        SQLEnum(CancellationStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=CancellationStatus.PROCESSED,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())

    booking: Mapped["Booking"] = relationship("Booking", back_populates="cancellation")
    cancelled_by: Mapped["User | None"] = relationship("User", foreign_keys=[cancelled_by_id])

    def __init__(self, **kw: Any):
        role_in = kw.pop("cancelled_by_role", None)
        actor = kw.get("cancelled_by")
        actor_id = kw.get("cancelled_by_id")
        actual_actor_id = actor_id if actor_id is not None else getattr(actor, "id", None)

        if role_in is not None:
            role = CancellationActorRole(role_in)
        else:
            role = CancellationActorRole.SYSTEM if actual_actor_id is None else CancellationActorRole.STUDENT

        self._validate_actor(role, actual_actor_id, actor is not None)
        self._cancelled_by_role = role

        # Thuộc tính dẫn xuất / tương thích ngược
        self._hours_before_session = Decimal(str(kw.pop("hours_before_session", "0.00")))
        self._refund_amount = Decimal(str(kw.pop("refund_amount", "0.00")))
        self._compensation_amount = Decimal(str(kw.pop("compensation_amount", "0.00")))
        self._penalty_amount = Decimal(str(kw.pop("penalty_amount", "0.00")))
        self._penalty_shortfall = Decimal(str(kw.pop("penalty_shortfall", "0.00")))

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
        return cls(booking_id=booking_id, cancelled_by_id=None, cancelled_by_role=CancellationActorRole.SYSTEM, **details)

    @property
    def cancelled_by_role(self) -> CancellationActorRole:
        if hasattr(self, "_cancelled_by_role") and self._cancelled_by_role is not None:
            return self._cancelled_by_role
        if self.cancelled_by_id is None:
            return CancellationActorRole.SYSTEM
        if self.cancelled_by and hasattr(self.cancelled_by, "role"):
            role_val = self.cancelled_by.role.value if hasattr(self.cancelled_by.role, "value") else self.cancelled_by.role
            return CancellationActorRole(role_val)
        return CancellationActorRole.STUDENT

    @cancelled_by_role.setter
    def cancelled_by_role(self, val: Any) -> None:
        self._cancelled_by_role = CancellationActorRole(val) if val else CancellationActorRole.STUDENT

    @property
    def hours_before_session(self) -> Decimal:
        if hasattr(self, "_hours_before_session") and self._hours_before_session is not None:
            return Decimal(str(self._hours_before_session))
        if self.booking and getattr(self.booking, "slot", None) and self.cancelled_at:
            diff = self.booking.slot.start_time - self.cancelled_at
            return Decimal(str(round(diff.total_seconds() / 3600.0, 2)))
        return Decimal("0.00")

    @hours_before_session.setter
    def hours_before_session(self, val: Any) -> None:
        self._hours_before_session = Decimal(str(val)) if val is not None else Decimal("0.00")

    @property
    def refund_amount(self) -> Decimal:
        return getattr(self, "_refund_amount", Decimal("0.00"))

    @refund_amount.setter
    def refund_amount(self, val: Any) -> None:
        self._refund_amount = Decimal(str(val)) if val is not None else Decimal("0.00")

    @property
    def compensation_amount(self) -> Decimal:
        return getattr(self, "_compensation_amount", Decimal("0.00"))

    @compensation_amount.setter
    def compensation_amount(self, val: Any) -> None:
        self._compensation_amount = Decimal(str(val)) if val is not None else Decimal("0.00")

    @property
    def penalty_amount(self) -> Decimal:
        return getattr(self, "_penalty_amount", Decimal("0.00"))

    @penalty_amount.setter
    def penalty_amount(self, val: Any) -> None:
        self._penalty_amount = Decimal(str(val)) if val is not None else Decimal("0.00")

    @property
    def penalty_shortfall(self) -> Decimal:
        return getattr(self, "_penalty_shortfall", Decimal("0.00"))

    @penalty_shortfall.setter
    def penalty_shortfall(self, val: Any) -> None:
        self._penalty_shortfall = Decimal(str(val)) if val is not None else Decimal("0.00")

    @property
    def is_system_cancellation(self) -> bool:
        return self.cancelled_by_role == CancellationActorRole.SYSTEM

    @property
    def cancelled_by_role_value(self) -> str:
        role = self.cancelled_by_role
        return role.value if isinstance(role, CancellationActorRole) else str(role)
