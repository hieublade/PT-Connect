from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.cancellation import Cancellation
from app.models.enums import BookingStatus, PaymentStatus, PaymentType, Role
from app.repositories.booking_repo import BookingRepository
from app.repositories.payment_repo import PaymentRepository
from app.repositories.user_repo import UserRepository
from app.schemas.responses.admin import (
    AdminBookingAnalyticsResponse,
    AdminPaymentAnalyticsResponse,
    AdminStatisticsResponse,
    PageResponse,
)


class AdminStatisticsService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.booking_repo = BookingRepository(db)
        self.payment_repo = PaymentRepository(db)

    def get_statistics(self) -> AdminStatisticsResponse:
        total_students = self.user_repo.count_by_role(Role.STUDENT)
        total_pts = self.user_repo.count_by_role(Role.PT)
        total_bookings = self.booking_repo.count()
        total_revenue = self.payment_repo.sum_amount_by_payment_type_and_status(
            PaymentType.PURCHASE_PACKAGE, PaymentStatus.SUCCESS
        )

        return AdminStatisticsResponse(
            total_students=total_students,
            total_pts=total_pts,
            total_bookings=total_bookings,
            total_revenue=total_revenue,
        )

    def _map_booking_row(
        self, row: tuple[Booking, Cancellation | None]
    ) -> AdminBookingAnalyticsResponse:
        b, cancel = row
        cancelled_by = None
        reason = None
        if cancel is not None:
            cancelled_by = cancel.cancelled_by_role if cancel.cancelled_by_role else "STUDENT"
            reason = cancel.reason
        elif b.status == BookingStatus.CANCELLED:
            cancelled_by = "STUDENT"
        return AdminBookingAnalyticsResponse.from_entity(b, cancelled_by, reason)

    def get_booking_analytics(self) -> list[AdminBookingAnalyticsResponse]:
        rows = self.booking_repo.find_bookings_with_cancellation()
        return [self._map_booking_row(row) for row in rows]

    def get_booking_analytics_page(
        self, page: int = 0, size: int = 20
    ) -> PageResponse[AdminBookingAnalyticsResponse]:
        rows, total = self.booking_repo.find_bookings_with_cancellation_page(page, size)
        items = [self._map_booking_row(row) for row in rows]
        return PageResponse.create(items, total, page, size)

    def get_payment_analytics(self) -> list[AdminPaymentAnalyticsResponse]:
        payments = self.payment_repo.find_all()
        return [AdminPaymentAnalyticsResponse.from_entity(p) for p in payments if p]

    def get_payment_analytics_page(
        self, page: int = 0, size: int = 20
    ) -> PageResponse[AdminPaymentAnalyticsResponse]:
        payments, total = self.payment_repo.find_page(page, size)
        items = [AdminPaymentAnalyticsResponse.from_entity(p) for p in payments if p]
        return PageResponse.create(items, total, page, size)
