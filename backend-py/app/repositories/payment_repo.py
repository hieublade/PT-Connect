from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models.enums import PaymentStatus, PaymentType
from app.models.payment import Payment
from app.models.wallet import Wallet


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, payment_id: int) -> Payment | None:
        return (
            self.db.query(Payment)
            .options(
                selectinload(Payment.wallet).selectinload(Wallet.user),
                selectinload(Payment.enrollment),
            )
            .filter(Payment.id == payment_id)
            .first()
        )

    def find_by_wallet_id(self, wallet_id: int) -> list[Payment]:
        return (
            self.db.query(Payment)
            .options(
                selectinload(Payment.wallet).selectinload(Wallet.user),
                selectinload(Payment.enrollment),
            )
            .filter(Payment.wallet_id == wallet_id)
            .order_by(Payment.created_at.desc())
            .all()
        )

    def find_all(self) -> list[Payment]:
        return (
            self.db.query(Payment)
            .options(
                selectinload(Payment.wallet).selectinload(Wallet.user),
                selectinload(Payment.enrollment),
            )
            .order_by(Payment.created_at.desc())
            .all()
        )

    def count(self) -> int:
        return self.db.query(func.count(Payment.id)).scalar() or 0

    def find_page(self, page: int = 0, size: int = 20) -> tuple[list[Payment], int]:
        total = self.count()
        offset = page * size
        items = (
            self.db.query(Payment)
            .options(
                selectinload(Payment.wallet).selectinload(Wallet.user),
                selectinload(Payment.enrollment),
            )
            .order_by(Payment.created_at.desc())
            .offset(offset)
            .limit(size)
            .all()
        )
        return items, total

    def sum_amount_by_payment_type_and_status(
        self, payment_type: PaymentType, status: PaymentStatus
    ) -> Decimal:
        result = (
            self.db.query(func.coalesce(func.sum(Payment.amount), 0))
            .filter(Payment.payment_type == payment_type, Payment.status == status)
            .scalar()
        )
        return Decimal(str(result)) if result is not None else Decimal("0.00")

    def save(self, payment: Payment) -> Payment:
        self.db.add(payment)
        self.db.flush()
        return payment
