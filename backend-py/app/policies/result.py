from dataclasses import dataclass
from decimal import Decimal


@dataclass
class CancellationCalculationResult:
    restore_session: bool
    refund_amount: Decimal = Decimal("0.00")
    compensation_amount: Decimal = Decimal("0.00")
    penalty_amount: Decimal = Decimal("0.00")
    penalty_shortfall: Decimal = Decimal("0.00")
    hours_before_session: Decimal = Decimal("0.00")
    explanation: str = ""
