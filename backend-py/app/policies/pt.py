from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from app.models.booking import Booking
from app.models.enums import BookingStatus, BookingType, Role
from app.policies.base import BaseCancellationPolicy
from app.policies.result import CancellationCalculationResult


class PtCancellationPolicy(BaseCancellationPolicy):
    ADVANCE_NOTICE_HOURS = 24.0
    COMPENSATION_RATE = Decimal("0.20")
    PENALTY_RATE = Decimal("0.20")

    def get_supported_role(self) -> Role:
        return Role.PT

    def calculate(
        self,
        booking: Booking,
        cancel_time: datetime | None = None,
        reason: str | None = None,
        evidence_url: str | None = None,
    ) -> CancellationCalculationResult:
        session_fee = booking.session_fee if booking.session_fee is not None else Decimal("0.00")
        is_package = booking.booking_type == BookingType.PACKAGE
        hours_before = self.calculate_hours_before(booking, cancel_time)

        # 1. Trường hợp từ chối lịch PENDING
        if booking.status == BookingStatus.PENDING:
            return CancellationCalculationResult(
                restore_session=is_package,
                refund_amount=session_fee if is_package else Decimal("0.00"),
                compensation_amount=Decimal("0.00"),
                penalty_amount=Decimal("0.00"),
                hours_before_session=hours_before,
                explanation="Huấn luyện viên từ chối ca tập khi đang chờ duyệt. Hoàn lại 1 buổi cho học viên, không phạt.",
            )

        # 2. Ca tập đã CONFIRMED và PT hủy trước >= 24 giờ
        if float(hours_before) >= self.ADVANCE_NOTICE_HOURS:
            return CancellationCalculationResult(
                restore_session=is_package,
                refund_amount=session_fee if is_package else Decimal("0.00"),
                compensation_amount=Decimal("0.00"),
                penalty_amount=Decimal("0.00"),
                hours_before_session=hours_before,
                explanation="Huấn luyện viên hủy trước giờ tập >= 24 giờ. Hoàn lại 1 buổi cho học viên, không phạt hay đền bù.",
            )

        # 3. Ca tập đã CONFIRMED và PT hủy sát giờ (< 24 giờ)
        compensation = (
            (session_fee * self.COMPENSATION_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if is_package
            else Decimal("0.00")
        )
        penalty = (
            (session_fee * self.PENALTY_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if is_package
            else Decimal("0.00")
        )

        return CancellationCalculationResult(
            restore_session=is_package,
            refund_amount=session_fee if is_package else Decimal("0.00"),
            compensation_amount=compensation,
            penalty_amount=penalty,
            hours_before_session=hours_before,
            explanation=(
                f"Huấn luyện viên hủy sát giờ (< 24 giờ). Hoàn 1 buổi cho học viên, đền bù 20% ({compensation} đ) "
                f"vào ví Học viên và phạt 20% ({penalty} đ) trừ từ ví Huấn luyện viên."
            ),
        )
