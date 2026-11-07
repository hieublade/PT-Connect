from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_roles
from app.core.responses import created_response, ok_response
from app.models.enums import BookingStatus, Role
from app.models.user import User
from app.schemas.requests.booking import (
    CancelBookingRequest,
    CreateBookingRequest,
    RejectBookingRequest,
)
from app.services.booking_service import BookingService

router = APIRouter(tags=["Bookings"])


# -------------------------------------------------------------
# Student & General Bookings
# -------------------------------------------------------------

@router.post("/bookings", status_code=201)
def create_booking(
    request: CreateBookingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.STUDENT)),
):
    service = BookingService(db)
    res = service.create_booking(current_user.email, request)
    return created_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Đặt lịch ca tập thành công",
        status_code=201,
    )


# Declare /my before /{id} to prevent path conflict
@router.get("/bookings/my")
def get_my_bookings(
    status: BookingStatus | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.STUDENT)),
):
    service = BookingService(db)
    bookings = service.get_my_bookings(current_user.email, status)
    return ok_response(
        data=[b.model_dump(mode="json", by_alias=True) for b in bookings],
        message="Lấy danh sách ca tập của học viên thành công",
    )


@router.get("/bookings/{id}/cancel-preview")
def preview_cancel_booking(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BookingService(db)
    preview = service.preview_cancel_booking(current_user.email, id)
    return ok_response(
        data=preview.model_dump(mode="json", by_alias=True),
        message="Xem trước chính sách hủy lịch thành công",
    )


@router.put("/bookings/{id}/cancel")
def cancel_booking_by_student(
    id: int,
    body: CancelBookingRequest | None = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BookingService(db)
    res = service.cancel_booking_by_student(current_user.email, id, body)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Học viên hủy ca tập thành công theo chính sách",
    )


@router.get("/bookings/{id}")
def get_booking_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BookingService(db)
    res = service.get_booking_by_id(current_user.email, id)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Lấy thông tin ca tập thành công",
    )


# -------------------------------------------------------------
# PT Bookings
# -------------------------------------------------------------

@router.get("/pt/bookings")
def get_pt_bookings(
    status: BookingStatus | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = BookingService(db)
    bookings = service.get_pt_bookings(current_user.email, status)
    return ok_response(
        data=[b.model_dump(mode="json", by_alias=True) for b in bookings],
        message="Lấy danh sách ca tập của Huấn luyện viên thành công",
    )


@router.put("/pt/bookings/{id}/confirm")
def confirm_booking(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = BookingService(db)
    res = service.confirm_booking(current_user.email, id)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Xác nhận ca tập thành công",
    )


@router.put("/pt/bookings/{id}/reject")
def reject_booking(
    id: int,
    body: RejectBookingRequest | None = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = BookingService(db)
    res = service.reject_booking(current_user.email, id, body)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Đã từ chối đơn đặt lịch và hoàn lại buổi tập",
    )


@router.put("/pt/bookings/{id}/cancel")
def cancel_booking_by_pt(
    id: int,
    body: CancelBookingRequest | None = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = BookingService(db)
    res = service.cancel_booking_by_pt(current_user.email, id, body)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Huấn luyện viên hủy ca tập thành công theo chính sách",
    )
