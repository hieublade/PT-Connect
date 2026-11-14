from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, ResourceNotFoundException, ForbiddenException
from app.models.dispute import BookingDispute
from app.models.enums import DisputeStatus, DisputeType, Role, PaymentType, PaymentMethod, BookingStatus
from app.models.user import User
from app.repositories.booking_repo import BookingRepository
from app.repositories.dispute_repo import DisputeRepository
from app.repositories.wallet_repo import WalletRepository
from app.schemas.requests.dispute import (
    CreateDisputeRequest,
    CounterDisputeRequest,
    RequestEvidenceRequest,
    ResolveDisputeRequest,
)
from app.schemas.responses.dispute import DisputeResponse


class DisputeService:
    def __init__(self, db: Session):
        self.db = db
        self.dispute_repo = DisputeRepository(db)
        self.booking_repo = BookingRepository(db)
        self.wallet_repo = WalletRepository(db)

    def _to_response(self, d: BookingDispute) -> DisputeResponse:
        student_name = None
        student_id = None
        pt_id = None
        pt_name = None
        start_time = None
        end_time = None

        if d.booking:
            student_id = d.booking.student_id
            if d.booking.student:
                student_name = d.booking.student.full_name
            if d.booking.slot:
                start_time = d.booking.slot.start_time
                end_time = d.booking.slot.end_time
                if d.booking.slot.pt:
                    pt_id = d.booking.slot.pt.id
                    if d.booking.slot.pt.pt:
                        pt_name = d.booking.slot.pt.pt.full_name

        sender_name = d.sender.full_name if d.sender else None

        return DisputeResponse(
            id=d.id,
            booking_id=d.booking_id,
            sender_id=d.sender_id,
            sender_role=d.sender_role,
            sender_name=sender_name,
            dispute_type=d.dispute_type,
            reason=d.reason,
            evidence_url=d.evidence_url,
            counter_evidence_url=d.counter_evidence_url,
            counter_argument=d.counter_argument,
            status=d.status,
            admin_notes=d.admin_notes,
            deadline_at=d.deadline_at,
            resolved_at=d.resolved_at,
            created_at=d.created_at,
            student_id=student_id,
            student_name=student_name,
            pt_id=pt_id,
            pt_name=pt_name,
            start_time=start_time,
            end_time=end_time,
        )

    def create_dispute(self, user: User, req: CreateDisputeRequest) -> DisputeResponse:
        booking = self.booking_repo.get_by_id(req.booking_id)
        if not booking:
            raise ResourceNotFoundException(f"Không tìm thấy ca tập #{req.booking_id}")

        # Kiểm tra quyền: Phải là học viên hoặc PT của ca tập
        is_student = (booking.student_id == user.id)
        is_pt = (booking.slot and booking.slot.pt and booking.slot.pt.user_id == user.id)

        if not is_student and not is_pt and user.role != Role.ADMIN:
            raise ForbiddenException("Bạn không có quyền khiếu nại ca tập này")

        # 1. Ràng buộc: Mỗi ca tập chỉ được gửi khiếu nại tối đa 1 lần duy nhất, không cho gửi lại lần 2
        existing = self.dispute_repo.find_by_booking_id(req.booking_id)
        if existing:
            raise BadRequestException(
                f"Ca tập #{req.booking_id} này đã từng được gửi khiếu nại (Hồ sơ khiếu nại #{existing[0].id}). "
                "Theo quy định của sàn, mỗi ca tập chỉ được gửi khiếu nại tối đa 1 lần duy nhất và không thể gửi lại lần 2."
            )

        # 2. Ràng buộc: Ca tập bị hủy chỉ được khiếu nại trong vòng 2 ngày (48 giờ) kể từ lúc bị hủy
        if booking.status == BookingStatus.CANCELLED or booking.cancellation:
            cancel_time = None
            if booking.cancellation and booking.cancellation.cancelled_at:
                cancel_time = booking.cancellation.cancelled_at
            elif booking.updated_at:
                cancel_time = booking.updated_at

            if cancel_time:
                now = datetime.now() if cancel_time.tzinfo is None else datetime.now(cancel_time.tzinfo)
                if cancel_time.tzinfo is not None and now.tzinfo is None:
                    cancel_time = cancel_time.replace(tzinfo=None)
                elif cancel_time.tzinfo is None and now.tzinfo is not None:
                    now = now.replace(tzinfo=None)

                elapsed_seconds = (now - cancel_time).total_seconds()
                if elapsed_seconds > 48 * 3600:
                    hours_elapsed = elapsed_seconds / 3600.0
                    days_elapsed = hours_elapsed / 24.0
                    raise BadRequestException(
                        f"Ca tập này đã bị hủy cách đây {days_elapsed:.1f} ngày ({hours_elapsed:.1f} giờ). "
                        "Theo quy định, bạn chỉ được quyền gửi khiếu nại trong thời hạn tối đa 2 ngày (48 giờ) kể từ thời điểm ca tập bị hủy."
                    )

        sender_role = "STUDENT" if is_student else ("PT" if is_pt else "ADMIN")
        deadline = datetime.utcnow() + timedelta(hours=48)

        dispute = BookingDispute(
            booking_id=req.booking_id,
            sender_id=user.id,
            sender_role=sender_role,
            dispute_type=req.dispute_type,
            reason=req.reason,
            evidence_url=req.evidence_url,
            status=DisputeStatus.PENDING,
            deadline_at=deadline,
            created_at=datetime.utcnow(),
        )
        self.dispute_repo.create(dispute)
        self.db.commit()

        # Load lại với đầy đủ relationships
        created = self.dispute_repo.get_by_id(dispute.id)
        return self._to_response(created)

    def submit_counter_argument(self, dispute_id: int, user: User, req: CounterDisputeRequest) -> DisputeResponse:
        dispute = self.dispute_repo.get_by_id_with_lock(dispute_id)
        if not dispute:
            raise ResourceNotFoundException(f"Không tìm thấy khiếu nại #{dispute_id}")

        if dispute.status not in (DisputeStatus.PENDING, DisputeStatus.EVIDENCE_REQUESTED):
            raise BadRequestException("Khiếu nại này đã được đóng hoặc phân xử xong")

        # Đối phương gửi phản biện
        booking = dispute.booking
        if not booking:
            booking = self.booking_repo.get_by_id(dispute.booking_id)

        is_student = (booking.student_id == user.id)
        is_pt = (booking.slot and booking.slot.pt and booking.slot.pt.user_id == user.id)

        # Người phản biện phải là bên còn lại (không phải sender ban đầu)
        if dispute.sender_id == user.id:
            raise BadRequestException("Bạn là người gửi khiếu nại ban đầu, không thể gửi phản biện cho chính mình")

        if not is_student and not is_pt and user.role != Role.ADMIN:
            raise ForbiddenException("Bạn không phải bên liên quan trong vụ tranh chấp này")

        dispute.counter_argument = req.counter_argument
        if req.counter_evidence_url:
            dispute.counter_evidence_url = req.counter_evidence_url

        self.dispute_repo.update(dispute)
        self.db.commit()

        updated = self.dispute_repo.get_by_id(dispute.id)
        return self._to_response(updated)

    def request_more_evidence(self, dispute_id: int, admin: User, req: RequestEvidenceRequest) -> DisputeResponse:
        if admin.role != Role.ADMIN:
            raise ForbiddenException("Chỉ Quản trị viên mới có quyền yêu cầu thêm bằng chứng")

        dispute = self.dispute_repo.get_by_id_with_lock(dispute_id)
        if not dispute:
            raise ResourceNotFoundException(f"Không tìm thấy khiếu nại #{dispute_id}")

        dispute.status = DisputeStatus.EVIDENCE_REQUESTED
        dispute.admin_notes = req.admin_notes
        dispute.deadline_at = datetime.utcnow() + timedelta(hours=48)

        self.dispute_repo.update(dispute)
        self.db.commit()

        updated = self.dispute_repo.get_by_id(dispute.id)
        return self._to_response(updated)

    def resolve_dispute(self, dispute_id: int, admin: User, req: ResolveDisputeRequest) -> DisputeResponse:
        if admin.role != Role.ADMIN:
            raise ForbiddenException("Chỉ Quản trị viên mới có thẩm quyền phân xử khiếu nại")

        dispute = self.dispute_repo.get_by_id_with_lock(dispute_id)
        if not dispute:
            raise ResourceNotFoundException(f"Không tìm thấy khiếu nại #{dispute_id}")

        if dispute.status in (DisputeStatus.RESOLVED_REFUND, DisputeStatus.REJECTED):
            raise BadRequestException("Khiếu nại này đã được phân xử trước đó")

        action = req.action.upper().strip()
        booking = dispute.booking
        if not booking:
            booking = self.booking_repo.get_by_id(dispute.booking_id)

        if action == "RESOLVED_REFUND":
            # Chấp thuận hoàn trả 1 buổi tập
            if booking and booking.enrollment_id:
                enrollment = booking.enrollment
                if enrollment:
                    enrollment.remaining_sessions += 1
                    enrollment.status = "ACTIVE"
            if booking and booking.attendance and booking.attendance.status == "ABSENT":
                booking.attendance.status = "PRESENT"

            dispute.status = DisputeStatus.RESOLVED_REFUND

        elif action == "CONTRACT_TERMINATION":
            # Hủy toàn bộ hợp đồng và hoàn tiền các buổi còn lại cho học viên
            if booking and booking.enrollment:
                enroll = booking.enrollment
                rem_sessions = enroll.remaining_sessions
                if rem_sessions > 0 and enroll.total_sessions > 0:
                    refund_amount = (enroll.final_price / enroll.total_sessions) * rem_sessions
                    # Hoàn tiền vào ví học viên
                    student_wallet = self.wallet_repo.find_by_user_id(enroll.student_id)
                    if student_wallet:
                        student_wallet.balance += Decimal(str(refund_amount))
                enroll.status = "CANCELLED"
                enroll.remaining_sessions = 0

            dispute.status = DisputeStatus.RESOLVED_REFUND

        elif action == "REJECTED":
            dispute.status = DisputeStatus.REJECTED
        else:
            raise BadRequestException(f"Hành động phân xử '{action}' không hợp lệ")

        dispute.admin_notes = req.admin_notes
        dispute.resolved_at = datetime.utcnow()

        self.dispute_repo.update(dispute)
        self.db.commit()

        updated = self.dispute_repo.get_by_id(dispute.id)
        return self._to_response(updated)

    def list_disputes(self, user: User, status: DisputeStatus | None = None) -> list[DisputeResponse]:
        if user.role == Role.ADMIN:
            disputes = self.dispute_repo.find_all(status)
        else:
            disputes = self.dispute_repo.find_by_user_id(user.id)
            if status:
                disputes = [d for d in disputes if d.status == status]

        return [self._to_response(d) for d in disputes]

    def get_dispute(self, dispute_id: int, user: User) -> DisputeResponse:
        dispute = self.dispute_repo.get_by_id(dispute_id)
        if not dispute:
            raise ResourceNotFoundException(f"Không tìm thấy khiếu nại #{dispute_id}")

        if user.role != Role.ADMIN and dispute.sender_id != user.id:
            booking = dispute.booking
            is_student = (booking and booking.student_id == user.id)
            is_pt = (booking and booking.slot and booking.slot.pt and booking.slot.pt.user_id == user.id)
            if not is_student and not is_pt:
                raise ForbiddenException("Bạn không có quyền xem khiếu nại này")

        return self._to_response(dispute)
