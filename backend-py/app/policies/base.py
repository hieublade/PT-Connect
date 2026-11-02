from abc import ABC, abstractmethod
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from app.core.clock import now_local
from app.models.booking import Booking
from app.models.enums import Role
from app.policies.result import CancellationCalculationResult


class BaseCancellationPolicy(ABC):
    @abstractmethod
    def get_supported_role(self) -> Role:
        pass

    @abstractmethod
    def calculate(
        self,
        booking: Booking,
        cancel_time: datetime | None = None,
        reason: str | None = None,
        evidence_url: str | None = None,
    ) -> CancellationCalculationResult:
        pass

    def calculate_hours_before(
        self,
        booking: Booking,
        cancel_time: datetime | None = None,
    ) -> Decimal:
        if not booking.slot or not booking.slot.start_time:
            return Decimal("0.00")

        start_time = booking.slot.start_time
        effective_time = cancel_time if cancel_time is not None else now_local()

        if effective_time > start_time:
            return Decimal("0.00")

        # Java: long minutes = Duration.between(effectiveCancelTime, startTime).toMinutes();
        # double hours = Math.max(0.0, minutes / 60.0);
        # return BigDecimal.valueOf(hours).setScale(2, RoundingMode.HALF_UP);
        minutes = int((start_time - effective_time).total_seconds() // 60)
        hours = max(0.0, minutes / 60.0)
        return Decimal(str(hours)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
