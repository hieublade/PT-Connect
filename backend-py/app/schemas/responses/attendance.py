from app.models.attendance import Attendance
from app.models.enums import AttendanceStatus, VerificationMethod
from app.schemas.base import CamelModel, LocalDateTime


class StartAttendanceResponse(CamelModel):
    attendance_id: int
    booking_id: int
    otp_code: str
    check_in_time: LocalDateTime
    expires_at: LocalDateTime
    status: AttendanceStatus
    message: str


class AttendanceResponse(CamelModel):
    id: int
    booking_id: int | None = None
    check_in_time: LocalDateTime | None = None
    check_out_time: LocalDateTime | None = None
    verification_method: VerificationMethod
    student_confirmed: bool = False
    pt_confirmed: bool = False
    status: AttendanceStatus
    fully_confirmed: bool = False

    @classmethod
    def from_entity(cls, attendance: Attendance | None) -> "AttendanceResponse | None":
        if attendance is None:
            return None

        b_id = attendance.booking.id if attendance.booking else None
        return cls(
            id=attendance.id,
            booking_id=b_id,
            check_in_time=attendance.check_in_time,
            check_out_time=attendance.check_out_time,
            verification_method=attendance.verification_method,
            student_confirmed=attendance.student_confirmed,
            pt_confirmed=attendance.pt_confirmed,
            status=attendance.status,
            fully_confirmed=attendance.is_fully_confirmed(),
        )
