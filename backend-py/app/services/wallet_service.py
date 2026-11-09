import logging
import secrets
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, ResourceNotFoundException
from app.models.enrollment import Enrollment
from app.models.enums import PaymentMethod, PaymentStatus, PaymentType, WalletStatus
from app.models.payment import Payment
from app.models.user import User
from app.repositories.payment_repo import PaymentRepository
from app.repositories.user_repo import UserRepository
from app.repositories.wallet_repo import WalletRepository
from app.schemas.requests.wallet import TopupRequest, WithdrawRequest
from app.schemas.responses.wallet import PaymentResponse, WalletResponse

logger = logging.getLogger(__name__)


class WalletService:
    def __init__(self, db: Session):
        self.db = db
        self.wallet_repo = WalletRepository(db)
        self.user_repo = UserRepository(db)
        self.payment_repo = PaymentRepository(db)

    def _get_user_by_email(self, email: str) -> User:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise ResourceNotFoundException("Không tìm thấy thông tin tài khoản người dùng")
        return user

    def get_wallet(self, user_email: str) -> WalletResponse:
        user = self._get_user_by_email(user_email)
        wallet = self.wallet_repo.get_by_user_id(user.id)
        if not wallet:
            raise ResourceNotFoundException("Không tìm thấy ví của người dùng")

        payments = self.payment_repo.find_by_wallet_id(wallet.id)
        transactions = [PaymentResponse.from_entity(p) for p in payments if p]
        return WalletResponse.from_entity(wallet, transactions)

    def topup(self, user_email: str, request: TopupRequest) -> PaymentResponse:
        if request.amount is None or request.amount <= Decimal(0):
            raise BadRequestException("Số tiền nạp phải lớn hơn 0")

        user = self._get_user_by_email(user_email)
        wallet = self.wallet_repo.get_by_user_id(user.id)
        if not wallet:
            raise ResourceNotFoundException("Không tìm thấy ví của người dùng")

        wallet.credit(request.amount)
        self.wallet_repo.save(wallet)

        date_prefix = datetime.now().strftime("%Y%m%d")
        short_id = secrets.token_hex(4).upper()
        txn_ref = f"TXN_TOPUP_{date_prefix}_{short_id}"

        method = PaymentMethod.from_string(request.payment_method)

        payment = Payment(
            wallet_id=wallet.id,
            enrollment_id=None,
            amount=request.amount,
            payment_type=PaymentType.TOPUP,
            payment_method=method,
            status=PaymentStatus.SUCCESS,
            transaction_ref=txn_ref,
        )
        saved = self.payment_repo.save(payment)
        self.db.commit()
        self.db.refresh(saved)
        logger.info("Nạp tiền ví thành công cho user: %s, số tiền: %s, txnRef: %s", user_email, request.amount, txn_ref)
        return PaymentResponse.from_entity(saved)

    def withdraw(self, user_email: str, request: WithdrawRequest) -> PaymentResponse:
        if request.amount is None or request.amount <= Decimal(0):
            raise BadRequestException("Số tiền rút phải lớn hơn 0")

        user = self._get_user_by_email(user_email)
        wallet = self.wallet_repo.get_by_user_id(user.id)
        if not wallet:
            raise ResourceNotFoundException("Không tìm thấy ví của người dùng")

        if wallet.status != WalletStatus.ACTIVE:
            raise BadRequestException("Ví đang bị đóng băng hoặc tạm khóa, không thể rút tiền")

        available_balance = wallet.balance - wallet.locked_balance
        if available_balance < request.amount:
            raise BadRequestException(
                f"Số dư khả dụng ({float(available_balance):,.0f} VND) không đủ để rút {float(request.amount):,.0f} VND"
            )

        wallet.debit(request.amount)
        self.wallet_repo.save(wallet)

        date_prefix = datetime.now().strftime("%Y%m%d")
        short_id = secrets.token_hex(4).upper()
        txn_ref = f"TXN_WITHDRAW_{date_prefix}_{short_id}"

        payment = Payment(
            wallet_id=wallet.id,
            enrollment_id=None,
            amount=request.amount,
            payment_type=PaymentType.REFUND,
            payment_method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.SUCCESS,
            transaction_ref=txn_ref,
        )
        saved = self.payment_repo.save(payment)
        self.db.commit()
        self.db.refresh(saved)
        logger.info(
            "Rút tiền ví thành công cho user: %s, số tiền: %s, ngân hàng: %s, STK: %s, txnRef: %s",
            user_email,
            request.amount,
            request.bank_name,
            request.account_number,
            txn_ref,
        )
        return PaymentResponse.from_entity(saved)

    def process_course_purchase(
        self,
        user_id: int,
        enrollment: Enrollment,
        amount: Decimal,
        payment_method: PaymentMethod | str | None,
    ) -> Payment:
        if amount is None or amount <= Decimal(0):
            raise BadRequestException("Số tiền thanh toán khóa học phải lớn hơn 0")

        wallet = self.wallet_repo.get_by_user_id(user_id)
        if not wallet:
            raise ResourceNotFoundException(f"Không tìm thấy ví của học viên ID: {user_id}")

        if wallet.status != WalletStatus.ACTIVE:
            raise BadRequestException("Ví của bạn đang bị khóa, không thể giao dịch")

        wallet.debit(amount)
        self.wallet_repo.save(wallet)

        date_prefix = datetime.now().strftime("%Y%m%d")
        short_id = secrets.token_hex(4).upper()
        txn_ref = f"TXN_BUY_{date_prefix}_{short_id}"

        method = PaymentMethod.from_string(str(payment_method)) if payment_method else PaymentMethod.WALLET

        payment = Payment(
            wallet_id=wallet.id,
            enrollment_id=enrollment.id,
            amount=amount,
            payment_type=PaymentType.PURCHASE_PACKAGE,
            payment_method=method,
            status=PaymentStatus.SUCCESS,
            transaction_ref=txn_ref,
        )
        saved = self.payment_repo.save(payment)
        self.db.flush()
        logger.info("Thanh toán khóa học thành công cho user ID %s, số tiền: %s, txnRef: %s", user_id, amount, txn_ref)
        return saved

    def process_booking_compensation(
        self,
        user_id: int,
        enrollment: Enrollment | None,
        amount: Decimal,
    ) -> Payment | None:
        if amount is None or amount <= Decimal(0):
            return None

        wallet = self.wallet_repo.get_by_user_id(user_id)
        if not wallet:
            logger.warning("Không tìm thấy ví của user ID %s để đền bù ca tập", user_id)
            return None

        wallet.credit(amount)
        self.wallet_repo.save(wallet)

        date_prefix = datetime.now().strftime("%Y%m%d")
        short_id = secrets.token_hex(4).upper()
        txn_ref = f"TXN_COMP_{date_prefix}_{short_id}"

        payment = Payment(
            wallet_id=wallet.id,
            enrollment_id=enrollment.id if enrollment else None,
            amount=amount,
            payment_type=PaymentType.COMPENSATION,
            payment_method=PaymentMethod.WALLET,
            status=PaymentStatus.SUCCESS,
            transaction_ref=txn_ref,
        )
        saved = self.payment_repo.save(payment)
        self.db.flush()
        logger.info("Đã đền bù %s vào ví user ID %s, txnRef: %s", amount, user_id, txn_ref)
        return saved

    def process_booking_penalty(
        self,
        user_id: int,
        enrollment: Enrollment | None,
        amount: Decimal,
    ) -> Payment | None:
        if amount is None or amount <= Decimal(0):
            return None

        wallet = self.wallet_repo.get_by_user_id(user_id)
        if not wallet:
            logger.warning("Không tìm thấy ví của user ID %s để phạt ca tập", user_id)
            return None

        wallet.debit_penalty(amount)
        self.wallet_repo.save(wallet)

        date_prefix = datetime.now().strftime("%Y%m%d")
        short_id = secrets.token_hex(4).upper()
        txn_ref = f"TXN_PENALTY_{date_prefix}_{short_id}"

        # In Java, penalty payment has payment_type = REFUND
        payment = Payment(
            wallet_id=wallet.id,
            enrollment_id=enrollment.id if enrollment else None,
            amount=amount,
            payment_type=PaymentType.REFUND,
            payment_method=PaymentMethod.WALLET,
            status=PaymentStatus.SUCCESS,
            transaction_ref=txn_ref,
        )
        saved = self.payment_repo.save(payment)
        self.db.flush()
        logger.info("Đã trừ phạt %s từ ví user ID %s, txnRef: %s", amount, user_id, txn_ref)
        return saved
