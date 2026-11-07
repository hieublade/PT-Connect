import logging
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.clock import now_local
from app.core.exceptions import (
    BadRequestException,
    ResourceNotFoundException,
    UnauthorizedException,
)
from app.models.attendance import Attendance
from app.models.booking import Booking
from app.models.enums import AttendanceStatus, BookingStatus, BookingType, Role, VerificationMethod
from app.otp.store import otp_store
from app.repositories.attendance_repo import AttendanceRepository
from app.repositories.booking_repo import BookingRepository
from app.repositories.enrollment_repo import EnrollmentRepository
from app.repositories.pt_profile_repo import PTProfileRepository
from app.repositories.user_repo import UserRepository
from app.schemas.requests.attendance import StudentCheckInRequest
from app.schemas.responses.attendance import AttendanceResponse, StartAttendanceResponse

logger = logging.getLogger(__name__)


class AttendanceService:
    def __init__(self, db: Session):
        self.db = db
        self.attendance_repo = AttendanceRepository(db)
        self.booking_repo = BookingRepository(db)
        self.enrollment_repo = EnrollmentRepository(db)
        self.user_repo = UserRepository(db)
        self.pt_profile_repo = PTProfileRepository(db)

    def start_attendance(self, pt_email: str, booking_id: int) -> StartAttendanceResponse:
        user = self.user_repo.get_by_email(pt_email)
        if not user:
            raise ResourceNotFoundException(f"Không tìm thấy hồ sơ Huấn luyện viên cho email: {pt_email}")

        profile = self.pt_profile_repo.get_by_user_id(user.id)
        if not profile:
            raise ResourceNotFoundException(f"Không tìm thấy hồ sơ Huấn luyện viên cho email: {pt_email}")

        booking = self.booking_repo.get_by_id_with_lock(booking_id)
        if not booking:
            raise ResourceNotFoundException(f"Không tìm thấy đơn đặt lịch với ID: {booking_id}")

        if not booking.is_owned_by_pt(profile.id):
            raise BadRequestException("Bạn không có quyền thao tác trên đơn đặt lịch của Huấn luyện viên khác")

        if booking.status != BookingStatus.CONFIRMED:
            raise BadRequestException("Chỉ có thể điểm danh cho ca tập đã được xác nhận (CONFIRMED)")

        now = now_local()
        slot = booking.slot

        if slot and slot.start_time:
            if now < (slot.start_time - timedelta(minutes=15)):
                curr_str = now.strftime("%H:%M ngày %d/%m/%Y")
                slot_str = slot.start_time.strftime("%H:%M ngày %d/%m/%Y")
                raise BadRequestException(
                    f"Chưa đến thời gian bắt đầu ca tập (Hiện tại: {curr_str} - Ca tập bắt đầu lúc: {slot_str}). "
                    "Chỉ được mở điểm danh trước tối đa 15 phút."
                )

        is_late = False
        if slot and slot.start_time:
            if now > (slot.start_time + timedelta(minutes=15)):
                is_late = True

        status = AttendanceStatus.LATE if is_late else AttendanceStatus.PRESENT

        otp_code = otp_store.generate_otp(booking_id, 30)
        expires_at = now + timedelta(minutes=30)

        attendance = self.attendance_repo.get_by_booking_id(booking_id)
        if not attendance:
            attendance = Attendance(
                booking_id=booking.id,
                verification_method=VerificationMethod.OTP,
                student_confirmed=False,
                pt_confirmed=False,
            )

        attendance.check_in(now, VerificationMethod.OTP, late=is_late)
        saved = self.attendance_repo.save(attendance)
        self.db.commit()
        self.db.refresh(saved)

        logger.info("PT %s started attendance for booking %s, status=%s", pt_email, booking_id, status)

        return StartAttendanceResponse(
            attendance_id=saved.id,
            booking_id=booking.id,
            otp_code=otp_code,
            check_in_time=now,
            expires_at=expires_at,
            status=status,
            message=f"Mở phiên điểm danh thành công! Mã OTP là: {otp_code} (Hiệu lực trong 30 phút).",
        )

    def student_check_in(self, student_email: str, booking_id: int, request: StudentCheckInRequest) -> AttendanceResponse:
        student = self.user_repo.get_by_email(student_email)
        if not student:
            raise ResourceNotFoundException(f"Không tìm thấy học viên với email: {student_email}")

        booking = self.booking_repo.get_by_id_with_lock(booking_id)
        if not booking:
            raise ResourceNotFoundException(f"Không tìm thấy đơn đặt lịch với ID: {booking_id}")

        if booking.student_id != student.id:
            raise BadRequestException("Bạn không có quyền điểm danh cho đơn đặt lịch của học viên khác")

        if booking.status != BookingStatus.CONFIRMED:
            raise BadRequestException("Ca tập không ở trạng thái CONFIRMED để có thể điểm danh")

        attendance = self.attendance_repo.get_by_booking_id(booking_id)
        if not attendance:
            raise BadRequestException(
                "Huấn luyện viên chưa mở phiên điểm danh cho ca tập này. Vui lòng yêu cầu HLV bấm bắt đầu buổi tập."
            )

        if attendance.student_confirmed:
            raise BadRequestException("Bạn đã xác nhận điểm danh cho ca tập này rồi")

        if not otp_store.validate_otp(booking_id, request.otp_code):
            raise BadRequestException(
                "Mã OTP không chính xác hoặc đã hết thời gian hiệu lực. Vui lòng kiểm tra lại với Huấn luyện viên!"
            )

        attendance.confirm_by_student()

        if attendance.pt_confirmed:
            self._complete_session(booking, attendance)

        saved = self.attendance_repo.save(attendance)
        self.db.commit()
        self.db.refresh(saved)

        return AttendanceResponse.from_entity(saved)

    def pt_confirm_attendance(self, pt_email: str, booking_id: int) -> AttendanceResponse:
        user = self.user_repo.get_by_email(pt_email)
        if not user:
            raise ResourceNotFoundException(f"Không tìm thấy hồ sơ Huấn luyện viên cho email: {pt_email}")

        profile = self.pt_profile_repo.get_by_user_id(user.id)
        if not profile:
            raise ResourceNotFoundException(f"Không tìm thấy hồ sơ Huấn luyện viên cho email: {pt_email}")

        booking = self.booking_repo.get_by_id_with_lock(booking_id)
        if not booking:
            raise ResourceNotFoundException(f"Không tìm thấy đơn đặt lịch với ID: {booking_id}")

        if not booking.is_owned_by_pt(profile.id):
            raise BadRequestException("Bạn không có quyền thao tác trên ca tập của Huấn luyện viên khác")

        if booking.status != BookingStatus.CONFIRMED:
            raise BadRequestException("Ca tập không ở trạng thái CONFIRMED để xác nhận hoàn tất")

        attendance = self.attendance_repo.get_by_booking_id(booking_id)
        if not attendance:
            raise BadRequestException(
                "Chưa có phiên điểm danh cho ca tập này. Vui lòng bấm 'Bắt đầu điểm danh' trước."
            )

        attendance.confirm_by_pt()

        if attendance.student_confirmed:
            self._complete_session(booking, attendance)

        saved = self.attendance_repo.save(attendance)
        self.db.commit()
        self.db.refresh(saved)

        return AttendanceResponse.from_entity(saved)

    def mark_absent(self, pt_email: str, booking_id: int, reason: str = "Học viên vắng mặt không lý do") -> AttendanceResponse:
        user = self.user_repo.get_by_email(pt_email)
        if not user:
            raise ResourceNotFoundException(f"Không tìm thấy hồ sơ Huấn luyện viên cho email: {pt_email}")

        profile = self.pt_profile_repo.get_by_user_id(user.id)
        if not profile:
            raise ResourceNotFoundException(f"Không tìm thấy hồ sơ Huấn luyện viên cho email: {pt_email}")

        booking = self.booking_repo.get_by_id_with_lock(booking_id)
        if not booking:
            raise ResourceNotFoundException(f"Không tìm thấy đơn đặt lịch với ID: {booking_id}")

        if not booking.is_owned_by_pt(profile.id):
            raise BadRequestException("Bạn không có quyền thao tác trên ca tập của Huấn luyện viên khác")

        if booking.status != BookingStatus.CONFIRMED:
            raise BadRequestException("Chỉ có thể đánh dấu vắng mặt cho ca tập đang ở trạng thái CONFIRMED")

        now = now_local()
        attendance = self.attendance_repo.get_by_booking_id(booking_id)
        if not attendance:
            attendance = Attendance(
                booking_id=booking.id,
                verification_method=VerificationMethod.OTP,
            )

        attendance.mark_absent(now)

        self._complete_session(booking, attendance)
        saved = self.attendance_repo.save(attendance)
        self.db.commit()
        self.db.refresh(saved)

        return AttendanceResponse.from_entity(saved)

    def get_attendance_by_booking_id(self, user_email: str, booking_id: int) -> AttendanceResponse | None:
        user = self.user_repo.get_by_email(user_email)
        if not user:
            raise ResourceNotFoundException(f"Không tìm thấy người dùng với email: {user_email}")

        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise ResourceNotFoundException(f"Không tìm thấy đơn đặt lịch với ID: {booking_id}")

        is_student = booking.student_id == user.id
        is_pt = booking.pt and booking.pt.user_id == user.id
        is_admin = user.role == Role.ADMIN

        if not is_student and not is_pt and not is_admin:
            raise UnauthorizedException("Bạn không có quyền xem thông tin điểm danh của ca tập này")

        attendance = self.attendance_repo.get_by_booking_id(booking_id)
        return AttendanceResponse.from_entity(attendance)

    def _complete_session(self, booking: Booking, attendance: Attendance) -> None:
        attendance.check_out(now_local())
        booking.complete()
        self.booking_repo.save(booking)
        self.db.flush()

        otp_store.clear_otp(booking.id)

        # Check if enrollment is complete
        if booking.booking_type == BookingType.PACKAGE and booking.enrollment_id:
            enrollment = self.enrollment_repo.get_by_id(booking.enrollment_id)
            if enrollment and enrollment.remaining_sessions == 0:
                # Count open bookings excluding this one
                open_count = self.booking_repo.count_open_bookings_for_enrollment(enrollment.id, booking.id)
                if open_count == 0:
                    enrollment.complete()
                    self.enrollment_repo.save(enrollment)
                    logger.info("Enrollment %s completed!", enrollment.id)
