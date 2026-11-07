from app.models.enums import PaymentMethod, PaymentStatus, PaymentType, WalletStatus
from app.models.payment import Payment
from app.models.wallet import Wallet
from app.schemas.base import CamelModel, LocalDateTime, Money


class PaymentResponse(CamelModel):
    id: int
    wallet_id: int | None = None
    enrollment_id: int | None = None
    amount: Money
    payment_type: PaymentType
    payment_method: PaymentMethod
    status: PaymentStatus
    transaction_ref: str | None = None
    created_at: LocalDateTime | None = None

    @classmethod
    def from_entity(cls, payment: Payment | None) -> "PaymentResponse | None":
        if payment is None:
            return None

        w_id = payment.wallet.id if payment.wallet else None
        e_id = payment.enrollment.id if payment.enrollment else None

        return cls(
            id=payment.id,
            wallet_id=w_id,
            enrollment_id=e_id,
            amount=payment.amount,
            payment_type=payment.payment_type,
            payment_method=payment.payment_method,
            status=payment.status,
            transaction_ref=payment.transaction_ref,
            created_at=payment.created_at,
        )


class WalletResponse(CamelModel):
    id: int
    user_id: int | None = None
    balance: Money
    locked_balance: Money
    currency: str = "VND"
    status: WalletStatus
    updated_at: LocalDateTime | None = None
    transactions: list[PaymentResponse] = []

    @classmethod
    def from_entity(cls, wallet: Wallet | None, transactions: list[PaymentResponse] | None = None) -> "WalletResponse | None":
        if wallet is None:
            return None

        u_id = wallet.user.id if wallet.user else None
        return cls(
            id=wallet.id,
            user_id=u_id,
            balance=wallet.balance,
            locked_balance=wallet.locked_balance,
            currency=wallet.currency,
            status=wallet.status,
            updated_at=wallet.updated_at,
            transactions=transactions or [],
        )
