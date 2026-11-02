from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.responses import ok_response
from app.models.user import User
from app.schemas.requests.attendance import StudentCheckInRequest
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/{booking_id}/start")
def start_attendance(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AttendanceService(db)
    res = service.start_attendance(current_user.email, booking_id)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Mở phiên điểm danh thành công",
    )


@router.post("/{booking_id}/student-checkin")
def student_check_in(
    booking_id: int,
    request: StudentCheckInRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AttendanceService(db)
    res = service.student_check_in(current_user.email, booking_id, request)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Học viên điểm danh thành công",
    )


@router.post("/{booking_id}/pt-confirm")
def pt_confirm_attendance(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AttendanceService(db)
    res = service.pt_confirm_attendance(current_user.email, booking_id)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Huấn luyện viên xác nhận điểm danh thành công",
    )


@router.post("/{booking_id}/absent")
def mark_absent(
    booking_id: int,
    reason: str = Query("Học viên vắng mặt không lý do"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AttendanceService(db)
    res = service.mark_absent(current_user.email, booking_id, reason)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Đã ghi nhận học viên vắng mặt (ABSENT)",
    )


@router.get("/{booking_id}")
def get_attendance_by_booking_id(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AttendanceService(db)
    res = service.get_attendance_by_booking_id(current_user.email, booking_id)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True) if res else None,
        message="Lấy thông tin điểm danh thành công",
    )
