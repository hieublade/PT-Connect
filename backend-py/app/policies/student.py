from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from app.models.booking import Booking
from app.models.enums import BookingStatus, BookingType, Role
from app.policies.base import BaseCancellationPolicy
from app.policies.result import CancellationCalculationResult


class StudentCancellationPolicy(BaseCancellationPolicy):
    ADVANCE_NOTICE_HOURS = 24.0
    COMPENSATION_RATE = Decimal("0.50")

    def get_supported_role(self) -> Role:
        return Role.STUDENT

    def calculate(
        self,
        booking: Booking,
        cancel_time: datetime | None = None,
        reason: str | None = None,
        evidence_url: str | None = None,
    ) -> CancellationCalculationResult:
        session_fee = booking.session_fee if booking.session_fee is not None else Decimal("0.00")

        # 1. Trường hợp học thử (TRIAL)
        if booking.booking_type == BookingType.TRIAL:
            return CancellationCalculationResult(
                restore_session=False,
                refund_amount=Decimal("0.00"),
                compensation_amount=Decimal("0.00"),
                penalty_amount=Decimal("0.00"),
                hours_before_session=self.calculate_hours_before(booking, cancel_time),
                explanation="Học viên hủy buổi học thử miễn phí (TRIAL). Khung giờ được giải phóng, không có buổi để hoàn.",
            )

        hours_before = self.calculate_hours_before(booking, cancel_time)

        # 2. Ca tập còn đang chờ duyệt (PENDING): Luôn hoàn buổi, không phạt
        if booking.status == BookingStatus.PENDING:
            return CancellationCalculationResult(
                restore_session=True,
                refund_amount=session_fee,
                compensation_amount=Decimal("0.00"),
                penalty_amount=Decimal("0.00"),
                hours_before_session=hours_before,
                explanation="Học viên hủy ca tập khi đang chờ duyệt (PENDING). Hoàn trả 1 buổi tập vào hợp đồng.",
            )

        # 3. Ca tập đã CONFIRMED và hủy trước >= 24 giờ
        if float(hours_before) >= self.ADVANCE_NOTICE_HOURS:
            return CancellationCalculationResult(
                restore_session=True,
                refund_amount=session_fee,
                compensation_amount=Decimal("0.00"),
                penalty_amount=Decimal("0.00"),
                hours_before_session=hours_before,
                explanation="Học viên hủy trước giờ tập >= 24 giờ. Hoàn trả 1 buổi tập vào hợp đồng, không phát sinh chi phí.",
            )

        # 4. Ca tập đã CONFIRMED và hủy sát giờ (< 24 giờ)
        compensation = (session_fee * self.COMPENSATION_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return CancellationCalculationResult(
            restore_session=False,
            refund_amount=Decimal("0.00"),
            compensation_amount=compensation,
            penalty_amount=Decimal("0.00"),
            hours_before_session=hours_before,
            explanation=f"Học viên hủy sát giờ (< 24 giờ). Mất buổi tập, đền bù 50% học phí ca tập ({compensation} đ) vào ví Huấn luyện viên.",
        )
