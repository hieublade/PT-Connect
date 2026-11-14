from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import FetchedValue, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from app.core.exceptions import InsufficientBalanceException
from app.db.base import Base
from app.models.enums import WalletStatus

if TYPE_CHECKING:
    from app.models.payment import Payment
    from app.models.user import User


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    balance: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    locked_balance: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="VND")
    status: Mapped[WalletStatus] = mapped_column(
        SQLEnum(WalletStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=WalletStatus.ACTIVE,
    )
    updated_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())

    user: Mapped["User"] = relationship("User", back_populates="wallet")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="wallet")

    def __init__(self, **kw):
        kw.setdefault("balance", Decimal("0.00"))
        kw.setdefault("locked_balance", Decimal("0.00"))
        kw.setdefault("currency", "VND")
        kw.setdefault("status", WalletStatus.ACTIVE)
        super().__init__(**kw)

    def credit(self, amount: Decimal) -> None:
        self._check_usable(amount)
        self.balance = self.balance + amount

    def debit(self, amount: Decimal) -> None:
        self._check_usable(amount)
        remaining_balance = self.balance - amount
        if remaining_balance < self.locked_balance:
            raise InsufficientBalanceException("Số dư khả dụng không đủ")
        self.balance = remaining_balance

    def debit_penalty(self, amount: Decimal) -> Decimal:
        self._check_usable(amount)
        usable_balance = max(self.balance - self.locked_balance, Decimal("0.00"))
        applied = min(amount, usable_balance)
        self.balance = self.balance - applied
        return applied

    def _check_usable(self, amount: Decimal | None) -> None:
        if self.status != WalletStatus.ACTIVE:
            raise IllegalStateException("Ví đang bị đóng băng")
        if amount is None or amount <= Decimal(0):
            raise IllegalArgumentException("Số tiền phải lớn hơn 0")


class IllegalStateException(RuntimeError):
    pass


class IllegalArgumentException(ValueError):
    pass


class WalletAuditLog(Base):
    __tablename__ = "wallet_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"), nullable=False)
    old_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    new_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    old_locked_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    new_locked_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    changed_amount: Mapped[Decimal] = column_property(new_balance - old_balance)
    changed_locked_amount: Mapped[Decimal] = column_property(new_locked_balance - old_locked_balance)
    action_type: Mapped[str] = mapped_column(String(30), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=FetchedValue())

    wallet: Mapped["Wallet"] = relationship("Wallet")
