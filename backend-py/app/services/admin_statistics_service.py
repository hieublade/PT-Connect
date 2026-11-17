from sqlalchemy import Integer, func
from sqlalchemy.orm import Session

from app.models.availability_slot import AvailabilitySlot
from app.models.booking import Booking
from app.models.cancellation import Cancellation
from app.models.enums import BookingStatus, PaymentStatus, PaymentType, Role
from app.models.pt_profile import PTProfile
from app.models.user import User
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
        penalty_amount = None
        penalty_shortfall = None
        if cancel is not None:
            cancelled_by = cancel.cancelled_by_role_value if cancel.cancelled_by_role else "STUDENT"
            reason = cancel.reason
            penalty_amount = cancel.penalty_amount
            penalty_shortfall = getattr(cancel, "penalty_shortfall", None)
        elif b.status == BookingStatus.CANCELLED:
            cancelled_by = "STUDENT"
        return AdminBookingAnalyticsResponse.from_entity(
            b, cancelled_by, reason, penalty_amount, penalty_shortfall
        )

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

    # ------------------------------------------------------------------ #
    #  Analytics aggregation methods (no Pandas – pure SQLAlchemy)        #
    # ------------------------------------------------------------------ #

    def get_booking_status_summary(self) -> dict:
        """Đếm số booking theo status và tính percentage cho từng trạng thái."""
        rows = (
            self.db.query(Booking.status, func.count(Booking.id).label("cnt"))
            .group_by(Booking.status)
            .all()
        )
        total = sum(r.cnt for r in rows)
        result: dict = {}
        for status in BookingStatus:
            result[status.value] = {"count": 0, "percentage": 0.0}
        for r in rows:
            key = r.status.value if hasattr(r.status, "value") else str(r.status)
            pct = round(r.cnt / total * 100, 2) if total > 0 else 0.0
            result[key] = {"count": r.cnt, "percentage": pct}
        return {"total": total, "breakdown": result}

    @property
    def _is_sqlite(self) -> bool:
        bind = self.db.get_bind()
        return bind is not None and bind.dialect.name == "sqlite"

    def get_monthly_revenue_trends(self) -> list[dict]:
        """Doanh thu (SUM session_fee) và số booking theo tháng (YYYY-MM), sắp xếp tăng dần."""
        month_expr = (
            func.strftime("%Y-%m", Booking.created_at)
            if self._is_sqlite
            else func.date_format(Booking.created_at, "%Y-%m")
        )
        rows = (
            self.db.query(
                month_expr.label("month"),
                func.count(Booking.id).label("booking_count"),
                func.sum(Booking.session_fee).label("revenue"),
            )
            .filter(Booking.created_at.isnot(None))
            .group_by(month_expr)
            .order_by(month_expr)
            .all()
        )
        return [
            {
                "month": r.month,
                "booking_count": r.booking_count,
                "revenue": float(r.revenue) if r.revenue is not None else 0.0,
            }
            for r in rows
        ]

    def get_top_pts_by_completion(self, limit: int = 10) -> list[dict]:
        """Top PT theo số ca COMPLETED. Trả về total_count và completion_rate."""
        # Tổng booking của mỗi PT (mọi status)
        total_subq = (
            self.db.query(
                AvailabilitySlot.pt_id.label("pt_id"),
                func.count(Booking.id).label("total_count"),
            )
            .join(Booking, Booking.slot_id == AvailabilitySlot.id)
            .group_by(AvailabilitySlot.pt_id)
            .subquery()
        )

        # Số ca COMPLETED của mỗi PT
        completed_subq = (
            self.db.query(
                AvailabilitySlot.pt_id.label("pt_id"),
                func.count(Booking.id).label("completed_count"),
            )
            .join(Booking, Booking.slot_id == AvailabilitySlot.id)
            .filter(Booking.status == BookingStatus.COMPLETED)
            .group_by(AvailabilitySlot.pt_id)
            .subquery()
        )

        rows = (
            self.db.query(
                PTProfile.id.label("pt_profile_id"),
                PTProfile.user_id.label("user_id"),
                User.full_name.label("full_name"),
                func.coalesce(completed_subq.c.completed_count, 0).label("completed_count"),
                func.coalesce(total_subq.c.total_count, 0).label("total_count"),
            )
            .join(User, User.id == PTProfile.user_id)
            .outerjoin(completed_subq, completed_subq.c.pt_id == PTProfile.id)
            .outerjoin(total_subq, total_subq.c.pt_id == PTProfile.id)
            .order_by(func.coalesce(completed_subq.c.completed_count, 0).desc())
            .limit(limit)
            .all()
        )

        result = []
        for r in rows:
            total = int(r.total_count) if r.total_count else 0
            completed = int(r.completed_count) if r.completed_count else 0
            rate = round(completed / total * 100, 2) if total > 0 else 0.0
            result.append(
                {
                    "pt_profile_id": r.pt_profile_id,
                    "user_id": r.user_id,
                    "full_name": r.full_name or "",
                    "completed_count": completed,
                    "total_count": total,
                    "completion_rate": rate,
                }
            )
        return result

    def get_cancellation_by_role(self) -> list[dict]:
        """Đếm số lần hủy lịch theo cancelled_by_role (STUDENT/PT/SYSTEM/ADMIN)."""
        rows = (
            self.db.query(
                Cancellation.cancelled_by_role.label("role"),
                func.count(Cancellation.id).label("count"),
            )
            .group_by(Cancellation.cancelled_by_role)
            .all()
        )
        total = sum(r.count for r in rows)
        return [
            {
                "cancelled_by": r.role.value if hasattr(r.role, "value") else str(r.role),
                "count": r.count,
                "percentage": round(r.count / total * 100, 2) if total > 0 else 0.0,
            }
            for r in rows
        ]

    def get_popular_training_hours(self) -> list[dict]:
        """Đếm booking theo giờ bắt đầu (0-23) của slot."""
        hour_expr = (
            func.cast(func.strftime("%H", AvailabilitySlot.start_time), Integer)
            if self._is_sqlite
            else func.hour(AvailabilitySlot.start_time)
        )
        rows = (
            self.db.query(
                hour_expr.label("hour"),
                func.count(Booking.id).label("count"),
            )
            .join(Booking, Booking.slot_id == AvailabilitySlot.id)
            .group_by(hour_expr)
            .order_by(hour_expr)
            .all()
        )
        # Trả về đủ 24 giờ (kể cả giờ 0 count)
        hour_map = {r.hour: r.count for r in rows if r.hour is not None}
        return [
            {"hour": h, "count": hour_map.get(h, 0)}
            for h in range(24)
        ]
