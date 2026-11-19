import logging
import secrets
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, ResourceNotFoundException
from app.models.cancellation import Cancellation
from app.models.enrollment import Enrollment
from app.models.enums import PaymentMethod, PaymentStatus, PaymentType, Role, WalletStatus
from app.models.payment import Payment
from app.models.user import User
from app.models.wallet import Wallet
from app.repositories.payment_repo import PaymentRepository
from app.repositories.user_repo import UserRepository
from app.repositories.wallet_repo import WalletRepository
from app.schemas.requests.wallet import TopupRequest, UserWithdrawRequest
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

        # Tính tổng khoản nợ tiền phạt chưa thanh toán (penalty_shortfall)
        penalty_debt = Decimal("0.00")

        return WalletResponse.from_entity(wallet, transactions, penalty_debt=penalty_debt)

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

        # Tự động cấn trừ nợ phạt nếu user đang nợ tiền phạt vi phạm hủy ca
        self.auto_settle_penalty_debt(user.id)

        return PaymentResponse.from_entity(saved)

    def withdraw(self, user_email: str, request: UserWithdrawRequest) -> PaymentResponse:
        if request.amount is None or request.amount < Decimal("50000.00"):
            raise BadRequestException("Hạn mức rút tiền tối thiểu là 50,000 VNĐ / lần rút")

        user = self._get_user_by_email(user_email)
        wallet = self.wallet_repo.get_by_user_id(user.id)
        if not wallet:
            raise ResourceNotFoundException("Không tìm thấy ví của người dùng")

        if wallet.status != WalletStatus.ACTIVE:
            raise BadRequestException("Ví của bạn đang bị khóa, không thể thực hiện rút tiền")

        # Tính tổng khoản nợ tiền phạt chưa thanh toán (penalty_shortfall)
        penalty_debt = Decimal("0.00")

        available_balance = max(Decimal("0.00"), wallet.balance - wallet.locked_balance - penalty_debt)
        if request.amount > available_balance:
            if penalty_debt > Decimal("0.00"):
                raise BadRequestException(
                    f"Bạn đang có khoản nợ phạt {penalty_debt:,.0f} đ chưa thanh toán. "
                    f"Số dư khả dụng để rút sau khi giữ lại ký quỹ và nợ phạt là {available_balance:,.0f} đ. "
                    f"Không đủ để rút {request.amount:,.0f} đ."
                )
            raise BadRequestException(
                f"Số dư khả dụng ({available_balance:,.0f} đ) không đủ để rút số tiền {request.amount:,.0f} đ"
            )

        wallet.balance -= request.amount
        self.wallet_repo.save(wallet)

        date_prefix = datetime.now().strftime("%Y%m%d")
        short_id = secrets.token_hex(4).upper()
        txn_ref = f"TXN_WD_{date_prefix}_{short_id}"

        payment = Payment(
            wallet_id=wallet.id,
            enrollment_id=None,
            amount=request.amount,
            payment_type=PaymentType.WITHDRAWAL,
            payment_method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.SUCCESS,
            transaction_ref=txn_ref,
        )
        saved = self.payment_repo.save(payment)
        self.db.commit()
        self.db.refresh(saved)
        logger.info(
            "Rút tiền ví thành công cho user: %s, số tiền: %s, ngân hàng: %s - STK: %s, txnRef: %s",
            user_email,
            request.amount,
            request.bank_name,
            request.account_number,
            txn_ref,
        )
        return PaymentResponse.from_entity(saved)

    def auto_settle_penalty_debt(self, user_id: int) -> Decimal:
        """Tự động cấn trừ các khoản nợ phạt (penalty_shortfall) bằng số dư ví khả dụng nếu có."""
        wallet = self.wallet_repo.get_by_user_id(user_id)
        if not wallet or wallet.balance <= Decimal("0.00"):
            return Decimal("0.00")
        return Decimal("0.00")

    def pay_penalty_debt(self, user_email: str) -> PaymentResponse:
        """Thanh toán khoản nợ tiền phạt vi phạm hủy lịch (penalty_shortfall) bằng số dư ví."""
        user = self._get_user_by_email(user_email)
        wallet = self.wallet_repo.get_by_user_id(user.id)
        if not wallet:
            raise ResourceNotFoundException("Không tìm thấy ví của người dùng")

        # Tìm tất cả các bản ghi cancellation còn nợ penalty_shortfall của user
        cancels = (
            self.db.query(Cancellation)
            .filter(
                Cancellation.cancelled_by_id == user.id,
            )
            .all()
        )
        unpaid_cancels = [c for c in cancels if c.penalty_shortfall > Decimal("0.00")]
        total_debt = sum((c.penalty_shortfall for c in unpaid_cancels), Decimal("0.00"))
        if total_debt <= Decimal("0.00"):
            raise BadRequestException("Bạn không có khoản nợ phạt nào cần thanh toán.")

        if wallet.balance < total_debt:
            raise BadRequestException(
                f"Số dư ví ({wallet.balance:,.0f} đ) không đủ để thanh toán khoản nợ phạt ({total_debt:,.0f} đ). "
                "Vui lòng nạp thêm tiền vào ví trước khi thanh toán nợ phạt."
            )

        wallet.balance -= total_debt
        self.wallet_repo.save(wallet)

        for c in unpaid_cancels:
            c.penalty_amount += c.penalty_shortfall
            c.penalty_shortfall = Decimal("0.00")
            self.db.add(c)

        date_prefix = datetime.now().strftime("%Y%m%d")
        short_id = secrets.token_hex(4).upper()
        txn_ref = f"TXN_PAY_PENALTY_{date_prefix}_{short_id}"

        payment = Payment(
            wallet_id=wallet.id,
            enrollment_id=None,
            amount=total_debt,
            payment_type=PaymentType.PENALTY,
            payment_method=PaymentMethod.WALLET,
            status=PaymentStatus.SUCCESS,
            transaction_ref=txn_ref,
        )
        saved = self.payment_repo.save(payment)
        self.db.commit()
        self.db.refresh(saved)
        logger.info("Thanh toán nợ phạt thành công cho user: %s, số tiền: %s, txnRef: %s", user_email, total_debt, txn_ref)
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
    ) -> tuple[Payment | None, Decimal]:
        """Trừ tiền phạt từ ví user. Trả về (Payment | None, applied_amount)."""
        if amount is None or amount <= Decimal(0):
            return None, Decimal("0.00")

        wallet = self.wallet_repo.get_by_user_id(user_id)
        if not wallet:
            logger.warning("Không tìm thấy ví của user ID %s để phạt ca tập", user_id)
            return None, Decimal("0.00")

        applied_amount = wallet.debit_penalty(amount)
        self.wallet_repo.save(wallet)

        if applied_amount <= Decimal(0):
            logger.warning("Ví user ID %s không đủ số dư khả dụng để trừ phạt (yêu cầu: %s)", user_id, amount)
            return None, Decimal("0.00")

        date_prefix = datetime.now().strftime("%Y%m%d")
        short_id = secrets.token_hex(4).upper()
        txn_ref = f"TXN_PENALTY_{date_prefix}_{short_id}"

        payment = Payment(
            wallet_id=wallet.id,
            enrollment_id=enrollment.id if enrollment else None,
            amount=applied_amount,
            payment_type=PaymentType.PENALTY,
            payment_method=PaymentMethod.WALLET,
            status=PaymentStatus.SUCCESS,
            transaction_ref=txn_ref,
        )
        saved = self.payment_repo.save(payment)
        self.db.flush()
        logger.info("Đã trừ phạt %s từ ví user ID %s, txnRef: %s", applied_amount, user_id, txn_ref)
        return saved, applied_amount

    def get_or_create_admin_wallet(self) -> Wallet | None:
        admin = self.db.query(User).filter(User.role == Role.ADMIN).first()
        if not admin:
            return None
        wallet = self.wallet_repo.get_by_user_id(admin.id)
        if not wallet:
            wallet = Wallet(
                user_id=admin.id,
                balance=Decimal("0.00"),
                locked_balance=Decimal("0.00"),
                currency="VND",
                status=WalletStatus.ACTIVE,
            )
            self.wallet_repo.save(wallet)
            self.db.flush()
        return wallet

    def process_session_payout(
        self,
        pt_user_id: int,
        enrollment: Enrollment | None,
        amount: Decimal,
        booking_id: int | None = None,
    ) -> Payment | None:
        if amount is None or amount <= Decimal("0.00"):
            return None

        commission_rate = Decimal("0.10")
        commission = (amount * commission_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        pt_earnings = amount - commission

        pt_wallet = self.wallet_repo.get_by_user_id(pt_user_id)
        pt_payment = None
        if pt_wallet:
            pt_wallet.credit(pt_earnings)
            self.wallet_repo.save(pt_wallet)

            date_prefix = datetime.now().strftime("%Y%m%d")
            short_id = secrets.token_hex(4).upper()
            ref_booking = f"_{booking_id}" if booking_id else ""
            txn_ref = f"TXN_EARN{ref_booking}_{date_prefix}_{short_id}"

            pt_payment = Payment(
                wallet_id=pt_wallet.id,
                enrollment_id=enrollment.id if enrollment else None,
                amount=pt_earnings,
                payment_type=PaymentType.EARNING,
                payment_method=PaymentMethod.WALLET,
                status=PaymentStatus.SUCCESS,
                transaction_ref=txn_ref,
            )
            self.payment_repo.save(pt_payment)
            logger.info("Đã thanh toán thù lao %s vào ví PT user ID %s, txnRef: %s", pt_earnings, pt_user_id, txn_ref)

            # Tự động cấn trừ nợ phạt nếu PT đang còn nợ khoản phạt vi phạm hủy lịch
            self.auto_settle_penalty_debt(pt_user_id)

        admin_wallet = self.get_or_create_admin_wallet()
        if admin_wallet and commission > Decimal("0.00"):
            admin_wallet.credit(commission)
            self.wallet_repo.save(admin_wallet)

            date_prefix = datetime.now().strftime("%Y%m%d")
            short_id = secrets.token_hex(4).upper()
            ref_booking = f"_{booking_id}" if booking_id else ""
            admin_txn_ref = f"TXN_COMMISSION{ref_booking}_{date_prefix}_{short_id}"

            admin_payment = Payment(
                wallet_id=admin_wallet.id,
                enrollment_id=enrollment.id if enrollment else None,
                amount=commission,
                payment_type=PaymentType.PLATFORM_FEE,
                payment_method=PaymentMethod.WALLET,
                status=PaymentStatus.SUCCESS,
                transaction_ref=admin_txn_ref,
            )
            self.payment_repo.save(admin_payment)
            logger.info("Sàn đã thu hoa hồng %s (10%%) vào ví Admin ID %s, txnRef: %s", commission, admin_wallet.user_id, admin_txn_ref)

        self.db.flush()
        return pt_payment

