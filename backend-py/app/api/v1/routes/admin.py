from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.core.responses import ok_response
from app.models.enums import Role
from app.models.user import User
from app.schemas.requests.auth import UpdateUserStatusRequest
from app.services.admin_pt_service import AdminPTService
from app.services.admin_statistics_service import AdminStatisticsService
from app.services.user_service import UserService

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_roles(Role.ADMIN))],
)


@router.get("/users")
def get_users(
    role: Role | None = Query(None),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = UserService(db)
    users = service.get_users_by_role(role) if role is not None else service.get_all_users()
    return ok_response(
        data=[u.model_dump(mode="json", by_alias=True) for u in users],
        message="Lấy danh sách người dùng thành công",
    )


@router.put("/users/{id}/status")
def update_user_status(
    id: int,
    request: UpdateUserStatusRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = UserService(db)
    user = service.update_user_status(id, request.status)
    return ok_response(
        data=user.model_dump(mode="json", by_alias=True),
        message="Cập nhật trạng thái người dùng thành công",
    )


@router.get("/pt/pending")
def get_pending_pts(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = AdminPTService(db)
    pending_list = service.get_pending_pts()
    return ok_response(
        data=[p.model_dump(mode="json", by_alias=True) for p in pending_list],
        message="Lấy danh sách PT chờ duyệt thành công",
    )


@router.put("/pt/{id}/approve")
def approve_pt(
    id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = AdminPTService(db)
    res = service.approve_pt(id)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Phê duyệt hồ sơ Huấn luyện viên thành công",
    )


@router.put("/pt/{id}/reject")
def reject_pt(
    id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = AdminPTService(db)
    res = service.reject_pt(id)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Từ chối hồ sơ Huấn luyện viên thành công",
    )


@router.get("/statistics")
def get_statistics(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = AdminStatisticsService(db)
    stats = service.get_statistics()
    return ok_response(
        data=stats.model_dump(mode="json", by_alias=True),
        message="Lấy thống kê hệ thống thành công",
    )


@router.get("/bookings/page")
def get_bookings_page(
    page: int = Query(0, ge=0),
    size: int = Query(20, gt=0),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = AdminStatisticsService(db)
    res = service.get_booking_analytics_page(page, size)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Lấy dữ liệu đặt lịch phân trang thành công",
    )


@router.get("/bookings")
def get_bookings_for_analytics(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = AdminStatisticsService(db)
    bookings = service.get_booking_analytics()
    return ok_response(
        data=[b.model_dump(mode="json", by_alias=True) for b in bookings],
        message="Lấy dữ liệu đặt lịch cho phân tích thành công",
    )


@router.get("/payments/page")
def get_payments_page(
    page: int = Query(0, ge=0),
    size: int = Query(20, gt=0),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = AdminStatisticsService(db)
    res = service.get_payment_analytics_page(page, size)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Lấy dữ liệu thanh toán phân trang thành công",
    )


@router.get("/payments")
def get_payments_for_analytics(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = AdminStatisticsService(db)
    payments = service.get_payment_analytics()
    return ok_response(
        data=[p.model_dump(mode="json", by_alias=True) for p in payments],
        message="Lấy dữ liệu thanh toán cho phân tích thành công",
    )
