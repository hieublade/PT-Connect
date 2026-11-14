import logging
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.clock import now_local, today_local
from app.core.exceptions import (
    BadRequestException,
    BookingConflictException,
    ResourceNotFoundException,
)
from app.models.booking import Booking
from app.models.cancellation import Cancellation
from app.models.enrollment import Enrollment
from app.models.enums import BookingStatus, BookingType, CancellationStatus, Role, SlotStatus
from app.models.user import User
from app.policies.factory import cancellation_policy_factory
from app.policies.result import CancellationCalculationResult
from app.repositories.booking_repo import BookingRepository
from app.repositories.cancellation_repo import CancellationRepository
from app.repositories.enrollment_repo import EnrollmentRepository
from app.repositories.pt_profile_repo import PTProfileRepository
from app.repositories.slot_repo import AvailabilitySlotRepository
from app.repositories.user_repo import UserRepository
from app.schemas.requests.booking import (
    CancelBookingRequest,
    CreateBookingRequest,
    RejectBookingRequest,
)
from app.schemas.responses.booking import BookingResponse, CancelPreviewResponse
from app.services.wallet_service import WalletService

logger = logging.getLogger(__name__)


class BookingService:
    def __init__(self, db: Session):
        self.db = db
        self.slot_repo = AvailabilitySlotRepository(db)
        self.booking_repo = BookingRepository(db)
        self.enrollment_repo = EnrollmentRepository(db)
        self.user_repo = UserRepository(db)
        self.pt_profile_repo = PTProfileRepository(db)
        self.cancellation_repo = CancellationRepository(db)
        self.wallet_service = WalletService(db)

    def create_booking(self, student_email: str, request: CreateBookingRequest) -> BookingResponse:
        student = self.user_repo.get_by_email(student_email)
        if not student:
            raise ResourceNotFoundException(f"Không tìm thấy học viên với email: {student_email}")

        # Tự động hủy các ca PENDING quá 4 tiếng (chống chiếm giữ slot)
        self.booking_repo.auto_cancel_stale_bookings()

        # Kiểm tra hạn mức chống găm giữ slot ảo: Tối đa 2 ca PENDING cùng lúc
        pending_count = self.booking_repo.count_pending_by_student(student.id)
        if pending_count >= 2:
            raise BadRequestException(
                "Chính sách chống giữ lịch ảo: Bạn chỉ được phép có tối đa 2 ca tập đang chờ HLV duyệt (PENDING) cùng lúc. "
                "Vui lòng chờ HLV duyệt hoặc hủy ca chờ cũ trước khi đặt tiếp."
            )

        # 1. Pessimistic lock on slot
        slot = self.slot_repo.get_by_id_with_lock(request.slot_id)
        if not slot:
            raise ResourceNotFoundException(f"Không tìm thấy khung giờ với ID: {request.slot_id}")

        if slot.status != SlotStatus.AVAILABLE:
            raise BookingConflictException("Khung giờ này đã được đặt hoặc không còn khả dụng")

        if slot.start_time < now_local():
            raise BadRequestException("Không thể đặt khung giờ đã trôi qua trong quá khứ")

        if self.booking_repo.exists_overlapping_booking_for_student(student.id, slot.start_time, slot.end_time):
            raise BadRequestException("Bạn đã có một ca tập khác trùng khung giờ này")

        booking_type = request.booking_type or BookingType.PACKAGE
        enrollment: Enrollment | None = None
        session_fee = Decimal("0.00")

        # 2. Check booking type rules
        if booking_type == BookingType.TRIAL:
            if self.booking_repo.exists_trial_by_student_and_pt(student.id, slot.pt_id):
                raise BadRequestException(
                    "Bạn đã từng đặt lịch học thử với Huấn luyện viên này. Mỗi học viên chỉ được học thử 1 lần."
                )
            session_fee = Decimal("0.00")
        else:
            if request.enrollment_id is None:
                raise BadRequestException("Cần chọn hợp đồng khóa học khi đặt lịch theo gói (PACKAGE)")

            enrollment = self.enrollment_repo.get_by_id_with_lock(request.enrollment_id)
            if not enrollment:
                raise ResourceNotFoundException(f"Không tìm thấy hợp đồng với ID: {request.enrollment_id}")

            if not enrollment.belongs_to_student(student.id):
                raise BadRequestException("Hợp đồng này không thuộc về bạn")

            if not enrollment.is_owned_by_pt(slot.pt_id):
                raise BadRequestException("Khung giờ không thuộc về Huấn luyện viên của hợp đồng này")

            if enrollment.status != "ACTIVE":
                raise BadRequestException("Hợp đồng này hiện không ở trạng thái hoạt động")

            today = today_local()
            if today > enrollment.end_date:
                raise BadRequestException("Hợp đồng khóa học đã hết hạn sử dụng")

            if slot.start_time.date() > enrollment.end_date:
                raise BadRequestException(
                    f"Khung giờ tập vượt quá thời hạn sử dụng của hợp đồng (Hạn chót: {enrollment.end_date})"
                )

            if enrollment.remaining_sessions <= 0:
                raise BadRequestException("Hợp đồng đã sử dụng hết số buổi tập")

            enrollment.consume_session()
            self.enrollment_repo.save(enrollment)

            if enrollment.total_sessions > 0 and enrollment.final_price is not None:
                session_fee = (enrollment.final_price / Decimal(enrollment.total_sessions)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )

        # 3. Create booking and enforce domain invariants (mirrors fk_booking_enroll_student)
        booking = Booking(
            student_id=student.id,
            slot=slot,
            enrollment=enrollment,
            booking_type=booking_type,
            status=BookingStatus.PENDING,
            session_fee=session_fee,
            student_note=request.student_note,
        )
        try:
            booking.ensure_consistent_with_enrollment()
        except ValueError as ex:
            self.db.rollback()
            raise BadRequestException(str(ex)) from ex
        self.db.add(booking)

        # 4. Mark slot as BOOKED
        try:
            slot.book()
            self.slot_repo.save(slot)
            self.db.flush()
            self.db.commit()
            self.db.refresh(booking)
        except IntegrityError as ex:
            self.db.rollback()
            logger.warning("Integrity error on booking insert: %s", ex)
            raise BookingConflictException("Khung giờ này vừa có người khác đặt trước, vui lòng chọn khung giờ khác")

        logger.info("Created booking %s for %s", booking.id, student_email)
        return BookingResponse.from_entity(booking)

    def get_my_bookings(self, student_email: str, status: BookingStatus | None = None) -> list[BookingResponse]:
        student = self.user_repo.get_by_email(student_email)
        if not student:
            raise ResourceNotFoundException(f"Không tìm thấy học viên với email: {student_email}")

        bookings = self.booking_repo.find_by_student_id(student.id, status)
        return [self._map_to_response(b) for b in bookings]

    def get_pt_bookings(self, pt_email: str, status: BookingStatus | None = None) -> list[BookingResponse]:
        user = self.user_repo.get_by_email(pt_email)
        if not user or user.role != Role.PT:
            raise ResourceNotFoundException(f"Không tìm thấy hồ sơ Huấn luyện viên cho email: {pt_email}")

        profile = self.pt_profile_repo.get_by_user_id(user.id)
        if not profile:
            raise ResourceNotFoundException(f"Không tìm thấy hồ sơ Huấn luyện viên cho email: {pt_email}")

        bookings = self.booking_repo.find_by_pt_id(profile.id, status)
        return [self._map_to_response(b) for b in bookings]

    def get_booking_by_id(self, user_email: str, booking_id: int) -> BookingResponse:
        user = self.user_repo.get_by_email(user_email)
        if not user:
            raise ResourceNotFoundException(f"Không tìm thấy tài khoản với email: {user_email}")

        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise ResourceNotFoundException(f"Không tìm thấy đơn đặt lịch với ID: {booking_id}")

        is_student = booking.student_id == user.id
        is_pt = booking.pt and booking.pt.user_id == user.id
        is_admin = user.role == Role.ADMIN

        if not is_student and not is_pt and not is_admin:
            raise BadRequestException("Bạn không có quyền xem thông tin chi tiết đơn đặt lịch này")

        return self._map_to_response(booking)

    def confirm_booking(self, pt_email: str, booking_id: int) -> BookingResponse:
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

        if booking.status != BookingStatus.PENDING:
            raise BadRequestException("Chỉ có thể xác nhận đơn đặt lịch đang ở trạng thái chờ duyệt (PENDING)")

        booking.confirm()
        self.booking_repo.save(booking)
        self.db.commit()
        self.db.refresh(booking)
        logger.info("PT %s confirmed booking %s", pt_email, booking.id)
        return self._map_to_response(booking)

    def reject_booking(self, pt_email: str, booking_id: int, request: RejectBookingRequest | None = None) -> BookingResponse:
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

        if booking.status != BookingStatus.PENDING:
            raise BadRequestException("Chỉ có thể từ chối đơn đặt lịch đang ở trạng thái chờ duyệt (PENDING)")

        reason = (
            request.reason.strip()
            if request and request.reason and request.reason.strip()
            else "Huấn luyện viên bận đột xuất"
        )

        policy = cancellation_policy_factory.get_policy(Role.PT)
        result = policy.calculate(booking, now_local(), reason, None)

        return self._execute_cancellation(booking, user, "PT", reason, None, result)

    def cancel_booking_by_student(
        self, student_email: str, booking_id: int, request: CancelBookingRequest | None = None
    ) -> BookingResponse:
        student = self.user_repo.get_by_email(student_email)
        if not student:
            raise ResourceNotFoundException(f"Không tìm thấy học viên với email: {student_email}")

        booking = self.booking_repo.get_by_id_with_lock(booking_id)
        if not booking:
            raise ResourceNotFoundException(f"Không tìm thấy đơn đặt lịch với ID: {booking_id}")

        if booking.student_id != student.id:
            raise BadRequestException("Bạn không có quyền hủy đơn đặt lịch của học viên khác")

        if booking.status == BookingStatus.CANCELLED:
            raise BadRequestException("Đơn đặt lịch này đã được hủy trước đó")

        if booking.status == BookingStatus.COMPLETED:
            raise BadRequestException("Không thể hủy ca tập đã hoàn thành")

        reason = (
            request.reason.strip()
            if request and request.reason and request.reason.strip()
            else "Học viên hủy lịch ca tập"
        )
        evidence_url = request.evidence_url if request else None

        policy = cancellation_policy_factory.get_policy(Role.STUDENT)
        result = policy.calculate(booking, now_local(), reason, evidence_url)

        return self._execute_cancellation(booking, student, "STUDENT", reason, evidence_url, result)

    def cancel_booking_by_pt(
        self, pt_email: str, booking_id: int, request: CancelBookingRequest | None = None
    ) -> BookingResponse:
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

        if booking.status == BookingStatus.CANCELLED:
            raise BadRequestException("Đơn đặt lịch này đã được hủy trước đó")

        if booking.status == BookingStatus.COMPLETED:
            raise BadRequestException("Không thể hủy ca tập đã hoàn thành")

        reason = (
            request.reason.strip()
            if request and request.reason and request.reason.strip()
            else "Huấn luyện viên hủy lịch ca tập"
        )
        evidence_url = request.evidence_url if request else None

        policy = cancellation_policy_factory.get_policy(Role.PT)
        result = policy.calculate(booking, now_local(), reason, evidence_url)

        return self._execute_cancellation(booking, user, "PT", reason, evidence_url, result)

    def _execute_cancellation(
        self,
        booking: Booking,
        cancelled_by: User,
        cancelled_by_role: str,
        reason: str,
        evidence_url: str | None,
        result: CancellationCalculationResult,
    ) -> BookingResponse:
        # 1. State transition
        booking.cancel()

        # 2. Release slot
        if booking.slot:
            booking.slot.release()
            self.slot_repo.save(booking.slot)

        # 3. Restore session if applicable (Lock enrollment theo thứ tự toàn cục)
        if booking.enrollment_id:
            # Khóa dòng enrollment trước khi cập nhật số buổi
            locked_enrollment = self.enrollment_repo.get_by_id_with_lock(booking.enrollment_id)
            if result.restore_session and booking.booking_type == BookingType.PACKAGE and locked_enrollment:
                locked_enrollment.restore_session()
                self.enrollment_repo.save(locked_enrollment)

        # 4. Handle wallet effects (xử lý phạt PT trước, tránh sinh tiền đền bù ảo)
        self._handle_wallet_effects(booking, cancelled_by_role, result)

        # 5. Record cancellation row
        cancellation = Cancellation.by_user(
            booking.id,
            cancelled_by,
            cancelled_by_role,
            reason=reason,
            hours_before_session=result.hours_before_session,
            refund_amount=result.refund_amount,
            compensation_amount=result.compensation_amount,
            penalty_amount=result.penalty_amount,
            penalty_shortfall=result.penalty_shortfall,
            evidence_url=evidence_url,
            status=CancellationStatus.PROCESSED,
        )
        self.cancellation_repo.save(cancellation)
        self.booking_repo.save(booking)
        self.db.commit()
        self.db.refresh(booking)

        return BookingResponse.from_entity(booking, cancellation)

    def _handle_wallet_effects(
        self,
        booking: Booking,
        cancelled_by_role: str,
        result: CancellationCalculationResult,
    ) -> None:
        if cancelled_by_role.upper() == "STUDENT":
            if result.compensation_amount > Decimal(0) and booking.pt and booking.pt.pt:
                self.wallet_service.process_booking_compensation(
                    booking.pt.pt.id,
                    booking.enrollment,
                    result.compensation_amount,
                )
        elif cancelled_by_role.upper() == "PT":
            # PT penalty must be processed FIRST to back student compensation
            penalty_applied = Decimal("0.00")
            if result.penalty_amount > Decimal(0) and booking.pt and booking.pt.pt:
                _, penalty_applied = self.wallet_service.process_booking_penalty(
                    booking.pt.pt.id,
                    booking.enrollment,
                    result.penalty_amount,
                )
            result.penalty_shortfall = result.penalty_amount - penalty_applied
            result.penalty_amount = penalty_applied

            # Học viên nhận tiền đền bù được bảo chứng từ tiền phạt thực thu của PT
            comp_to_give = min(result.compensation_amount, penalty_applied)
            result.compensation_amount = comp_to_give
            if comp_to_give > Decimal(0) and booking.student:
                self.wallet_service.process_booking_compensation(
                    booking.student.id,
                    booking.enrollment,
                    comp_to_give,
                )

    def preview_cancel_booking(self, user_email: str, booking_id: int) -> CancelPreviewResponse:
        user = self.user_repo.get_by_email(user_email)
        if not user:
            raise ResourceNotFoundException(f"Không tìm thấy người dùng với email: {user_email}")

        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise ResourceNotFoundException(f"Không tìm thấy đơn đặt lịch với ID: {booking_id}")

        role = Role.STUDENT
        if booking.pt and booking.pt.pt and booking.pt.pt.id == user.id:
            role = Role.PT
        elif user.role == Role.ADMIN:
            role = Role.ADMIN

        policy = cancellation_policy_factory.get_policy(role)
        result = policy.calculate(booking, now_local(), "Xem trước", None)

        role_str = role.value if hasattr(role, "value") else str(role)

        return CancelPreviewResponse(
            booking_id=booking_id,
            cancelled_by_role=role_str,
            hours_before_session=result.hours_before_session,
            restore_session=result.restore_session,
            refund_amount=result.refund_amount,
            compensation_amount=result.compensation_amount,
            penalty_amount=result.penalty_amount,
            explanation=result.explanation,
        )

    def _map_to_response(self, booking: Booking) -> BookingResponse:
        cancellation = None
        if booking.status == BookingStatus.CANCELLED:
            cancellation = self.cancellation_repo.get_by_booking_id(booking.id)
        return BookingResponse.from_entity(booking, cancellation)
