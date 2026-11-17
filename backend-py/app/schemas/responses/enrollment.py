from decimal import Decimal

from app.models.enrollment import Enrollment
from app.models.enums import EnrollmentStatus
from app.schemas.base import CamelModel, LocalDate, LocalDateTime, Money


class PurchaseEligibilityResponse(CamelModel):
    """
    Kết quả kiểm tra điều kiện mua khóa học.
    Frontend dùng để hiển thị badge đủ/thiếu tiền mà không cần tự tính toán.
    """

    can_purchase: bool
    """True nếu học viên đủ điều kiện mua, False nếu không đủ."""

    reason: str | None = None
    """Lý do không thể mua (None nếu can_purchase=True)."""

    wallet_balance: Decimal
    """Số dư ví hiện tại của học viên (VNĐ)."""

    course_price: Decimal
    """Giá gốc của khóa học (VNĐ)."""

    shortage: Decimal
    """Số tiền còn thiếu = max(0, coursePrice - walletBalance). 0 nếu đủ tiền."""


class EnrollmentResponse(CamelModel):
    id: int
    student_id: int | None = None
    student_name: str | None = None
    student_email: str | None = None
    course_id: int | None = None
    course_title: str | None = None
    pt_id: int | None = None
    pt_name: str | None = None
    training_location: str | None = None
    final_price: Money
    total_sessions: int
    remaining_sessions: int
    start_date: LocalDate
    end_date: LocalDate
    contract_url: str | None = None
    status: EnrollmentStatus
    created_at: LocalDateTime | None = None

    @classmethod
    def from_entity(cls, enrollment: Enrollment | None) -> "EnrollmentResponse | None":
        if enrollment is None:
            return None

        s_id = None
        s_name = None
        s_email = None
        if enrollment.student:
            s_id = enrollment.student.id
            s_name = enrollment.student.full_name
            s_email = enrollment.student.email

        c_id = None
        c_title = None
        if enrollment.course:
            c_id = enrollment.course.id
            c_title = enrollment.course.title

        p_id = None
        p_name = None
        if enrollment.pt:
            p_id = enrollment.pt.id
            if enrollment.pt.pt:
                p_name = enrollment.pt.pt.full_name

        return cls(
            id=enrollment.id,
            student_id=s_id,
            student_name=s_name,
            student_email=s_email,
            course_id=c_id,
            course_title=c_title,
            pt_id=p_id,
            pt_name=p_name,
            training_location=enrollment.training_location,
            final_price=enrollment.final_price,
            total_sessions=enrollment.total_sessions,
            remaining_sessions=enrollment.remaining_sessions,
            start_date=enrollment.start_date,
            end_date=enrollment.end_date,
            contract_url=enrollment.contract_url,
            status=enrollment.status,
            created_at=enrollment.created_at,
        )
