from enum import Enum


class Role(str, Enum):
    STUDENT = "STUDENT"
    PT = "PT"
    ADMIN = "ADMIN"


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    SUSPENDED = "SUSPENDED"


class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


# Alias for PT status as requested in migration specs
PTStatus = VerificationStatus


class WalletStatus(str, Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"


class CourseStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class EnrollmentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class SlotStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BOOKED = "BOOKED"
    LOCKED = "LOCKED"


class BookingType(str, Enum):
    TRIAL = "TRIAL"
    PACKAGE = "PACKAGE"


class BookingStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class CancellationStatus(str, Enum):
    PROCESSED = "PROCESSED"
    DISPUTED = "DISPUTED"
    RESOLVED = "RESOLVED"


class CancellationActorRole(str, Enum):
    """Vai trò người hủy tại thời điểm hủy (Audit Role Snapshot). SYSTEM không gắn với user nào."""

    STUDENT = "STUDENT"
    PT = "PT"
    ADMIN = "ADMIN"
    SYSTEM = "SYSTEM"

    @property
    def requires_user(self) -> bool:
        return self is not CancellationActorRole.SYSTEM


class AttendanceStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"


class VerificationMethod(str, Enum):
    OTP = "OTP"
    QR_CODE = "QR_CODE"
    GEO_LOCATION = "GEO_LOCATION"


class PaymentType(str, Enum):
    TOPUP = "TOPUP"
    PURCHASE_PACKAGE = "PURCHASE_PACKAGE"
    COMPENSATION = "COMPENSATION"
    REFUND = "REFUND"
    PENALTY = "PENALTY"
    PLATFORM_FEE = "PLATFORM_FEE"
    WITHDRAWAL = "WITHDRAWAL"


class DisputeType(str, Enum):
    WRONG_ABSENT = "WRONG_ABSENT"
    PT_NO_SHOW = "PT_NO_SHOW"
    STUDENT_NO_SHOW = "STUDENT_NO_SHOW"
    ATTITUDE_QUALITY = "ATTITUDE_QUALITY"
    CONTRACT_TERMINATION = "CONTRACT_TERMINATION"
    OTHER = "OTHER"


class DisputeStatus(str, Enum):
    PENDING = "PENDING"
    EVIDENCE_REQUESTED = "EVIDENCE_REQUESTED"
    RESOLVED_REFUND = "RESOLVED_REFUND"
    REJECTED = "REJECTED"


class PaymentMethod(str, Enum):
    WALLET = "WALLET"
    BANK_TRANSFER = "BANK_TRANSFER"
    CREDIT_CARD = "CREDIT_CARD"
    CASH = "CASH"

    @classmethod
    def from_string(cls, value: str | None) -> "PaymentMethod":
        if value is None:
            return cls.BANK_TRANSFER
        upper = str(value).strip().upper()
        if upper in ("VNPAY", "MOMO", "ZALOPAY", "QR", ""):
            return cls.BANK_TRANSFER
        for member in cls:
            if member.name.upper() == upper:
                return member
        return cls.BANK_TRANSFER


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
