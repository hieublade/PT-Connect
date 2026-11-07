from datetime import datetime
from decimal import Decimal

from app.models.booking import Booking
from app.models.enums import BookingType, Role
from app.policies.base import BaseCancellationPolicy
from app.policies.result import CancellationCalculationResult


class AdminCancellationPolicy(BaseCancellationPolicy):
    def get_supported_role(self) -> Role:
        return Role.ADMIN

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

        evidence_note = f" (Có kèm bằng chứng: {evidence_url})" if evidence_url and evidence_url.strip() else ""

        return CancellationCalculationResult(
            restore_session=is_package,
            refund_amount=session_fee if is_package else Decimal("0.00"),
            compensation_amount=Decimal("0.00"),
            penalty_amount=Decimal("0.00"),
            hours_before_session=hours_before,
            explanation=f"Quản trị viên hủy do sự cố bất khả kháng{evidence_note}. Khôi phục 1 buổi cho học viên, không phạt hay đền bù.",
        )
