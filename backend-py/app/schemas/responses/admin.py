from typing import Any, Generic, TypeVar

from app.models.enums import BookingStatus, BookingType, PaymentMethod, PaymentStatus, PaymentType
from app.schemas.base import CamelModel, LocalDateTime, Money

T = TypeVar("T")


class PageSort(CamelModel):
    empty: bool = True
    sorted: bool = False
    unsorted: bool = True


class PageableObject(CamelModel):
    page_number: int = 0
    page_size: int = 20
    sort: PageSort = PageSort()
    offset: int = 0
    paged: bool = True
    unpaged: bool = False


class PageResponse(CamelModel, Generic[T]):
    content: list[T] = []
    pageable: PageableObject = PageableObject()
    total_pages: int = 0
    total_elements: int = 0
    last: bool = True
    size: int = 20
    number: int = 0
    sort: PageSort = PageSort()
    number_of_elements: int = 0
    first: bool = True
    empty: bool = True

    @classmethod
    def create(cls, items: list[T], total: int, page: int, size: int) -> "PageResponse[T]":
        total_pages = (total + size - 1) // size if size > 0 else 0
        return cls(
            content=items,
            pageable=PageableObject(
                page_number=page,
                page_size=size,
                offset=page * size,
                paged=True,
                unpaged=False,
            ),
            total_pages=total_pages,
            total_elements=total,
            last=(page >= total_pages - 1) if total_pages > 0 else True,
            size=size,
            number=page,
            sort=PageSort(),
            number_of_elements=len(items),
            first=(page == 0),
            empty=(len(items) == 0),
        )


class AdminStatisticsResponse(CamelModel):
    total_students: int
    total_pts: int
    total_bookings: int
    total_revenue: Money


class AdminBookingAnalyticsResponse(CamelModel):
    id: int
    student_id: int | None = None
    student_name: str | None = None
    pt_id: int | None = None
    pt_name: str | None = None
    booking_type: BookingType
    status: BookingStatus
    start_time: LocalDateTime | None = None
    end_time: LocalDateTime | None = None
    session_fee: Money | None = None
    created_at: LocalDateTime | None = None
    cancelled_by: str | None = None
    cancellation_reason: str | None = None
    penalty_amount: Money | None = None
    penalty_shortfall: Money | None = None

    @classmethod
    def from_entity(
        cls,
        b: Any,
        cancelled_by: str | None = None,
        cancellation_reason: str | None = None,
        penalty_amount: Any = None,
        penalty_shortfall: Any = None,
    ) -> "AdminBookingAnalyticsResponse | None":
        if b is None:
            return None

        student_id = b.student_id or (b.student.id if getattr(b, "student", None) else None)
        student_name = b.student.full_name if getattr(b, "student", None) else None

        pt_id = b.pt_id or (b.pt.id if getattr(b, "pt", None) else None)
        pt_name = None
        if getattr(b, "pt", None) and getattr(b.pt, "pt", None):
            pt_name = b.pt.pt.full_name

        start_time = b.slot.start_time if getattr(b, "slot", None) else None
        end_time = b.slot.end_time if getattr(b, "slot", None) else None

        return cls(
            id=b.id,
            student_id=student_id,
            student_name=student_name,
            pt_id=pt_id,
            pt_name=pt_name,
            booking_type=b.booking_type,
            status=b.status,
            start_time=start_time,
            end_time=end_time,
            session_fee=b.session_fee,
            created_at=b.created_at,
            cancelled_by=cancelled_by,
            cancellation_reason=cancellation_reason,
            penalty_amount=penalty_amount,
            penalty_shortfall=penalty_shortfall,
        )


class AdminPaymentAnalyticsResponse(CamelModel):
    id: int
    wallet_id: int | None = None
    user_id: int | None = None
    user_name: str | None = None
    enrollment_id: int | None = None
    amount: Money
    payment_type: PaymentType
    payment_method: PaymentMethod
    status: PaymentStatus
    transaction_ref: str | None = None
    created_at: LocalDateTime | None = None

    @classmethod
    def from_entity(cls, p: Any) -> "AdminPaymentAnalyticsResponse | None":
        if p is None:
            return None

        wallet_id = p.wallet_id or (p.wallet.id if getattr(p, "wallet", None) else None)
        user_id = None
        user_name = None
        if getattr(p, "wallet", None) and getattr(p.wallet, "user", None):
            user_id = p.wallet.user.id
            user_name = p.wallet.user.full_name

        enrollment_id = p.enrollment_id or (p.enrollment.id if getattr(p, "enrollment", None) else None)

        return cls(
            id=p.id,
            wallet_id=wallet_id,
            user_id=user_id,
            user_name=user_name,
            enrollment_id=enrollment_id,
            amount=p.amount,
            payment_type=p.payment_type,
            payment_method=p.payment_method,
            status=p.status,
            transaction_ref=p.transaction_ref,
            created_at=p.created_at,
        )
