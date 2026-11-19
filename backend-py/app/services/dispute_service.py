from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.core.clock import now_local
from app.core.exceptions import BadRequestException, ResourceNotFoundException, ForbiddenException
from app.models.booking import Booking
from app.models.dispute import BookingDispute
from app.models.enums import DisputeStatus, DisputeType, Role, PaymentType, PaymentMethod, PaymentStatus, BookingStatus
from app.models.payment import Payment
from app.models.user import User
from app.repositories.booking_repo import BookingRepository
from app.repositories.dispute_repo import DisputeRepository
from app.repositories.wallet_repo import WalletRepository
from app.schemas.requests.dispute import (
    CreateDisputeRequest,
    CounterDisputeRequest,
    RequestEvidenceRequest,
    ResolveDisputeRequest,
    SubmitAdditionalEvidenceRequest,
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
        booking_id = req.booking_id
        if not booking_id and req.enrollment_id:
            list_b = self.booking_repo.find_by_enrollment_id(req.enrollment_id)
            if list_b:
                booking_id = list_b[0].id
            else:
                raise BadRequestException("Hợp đồng này chưa có ca tập nào để khởi tạo hồ sơ khiếu nại")

        if not booking_id:
            raise BadRequestException("Vui lòng cung cấp mã ca tập hoặc mã hợp đồng cần khiếu nại.")

        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise ResourceNotFoundException(f"Không tìm thấy ca tập #{booking_id}")

        # Kiểm tra quyền: Phải là học viên hoặc PT của ca tập
        is_student = (booking.student_id == user.id)
        is_pt = (booking.slot and booking.slot.pt and booking.slot.pt.user_id == user.id)

        if not is_student and not is_pt and user.role != Role.ADMIN:
            raise ForbiddenException("Bạn không có quyền khiếu nại ca tập này")

        # Ràng buộc trạng thái nghiêm ngặt: Chỉ có ca COMPLETED và CANCELLED mới được gửi khiếu nại
        if booking.status not in (BookingStatus.COMPLETED, BookingStatus.CANCELLED) and user.role != Role.ADMIN:
            raise BadRequestException(
                f"Chỉ có các ca tập đã Hoàn thành (COMPLETED) hoặc đã Bị hủy (CANCELLED) mới được phép gửi khiếu nại. "
                f"Ca tập hiện tại đang ở trạng thái {booking.status.value} nên không thể gửi khiếu nại."
            )

        # 1. Ràng buộc: Mỗi ca tập chỉ được gửi khiếu nại tối đa 1 lần duy nhất, không cho gửi lại lần 2
        existing = self.dispute_repo.find_by_booking_id(booking_id)
        if existing:
            raise BadRequestException(
                f"Ca tập #{booking_id} này đã từng được gửi khiếu nại (Hồ sơ khiếu nại #{existing[0].id}). "
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
                now = now_local()
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

        # 3. Ràng buộc: Ca tập đã hoàn thành chỉ được khiếu nại trong vòng 2 ngày (48 giờ) kể từ khi ca tập kết thúc
        if booking.status == BookingStatus.COMPLETED:
            completed_time = None
            if booking.attendance and booking.attendance.check_out_time:
                completed_time = booking.attendance.check_out_time
            elif booking.slot and booking.slot.end_time:
                completed_time = booking.slot.end_time
            elif booking.updated_at:
                completed_time = booking.updated_at

            if completed_time:
                now = now_local()
                if completed_time.tzinfo is not None and now.tzinfo is None:
                    completed_time = completed_time.replace(tzinfo=None)
                elif completed_time.tzinfo is None and now.tzinfo is not None:
                    now = now.replace(tzinfo=None)

                elapsed_seconds = (now - completed_time).total_seconds()
                if elapsed_seconds > 48 * 3600:
                    hours_elapsed = elapsed_seconds / 3600.0
                    days_elapsed = hours_elapsed / 24.0
                    raise BadRequestException(
                        f"Ca tập này đã kết thúc cách đây {days_elapsed:.1f} ngày ({hours_elapsed:.1f} giờ). "
                        "Theo quy định, bạn chỉ được quyền gửi khiếu nại trong thời hạn tối đa 2 ngày (48 giờ) kể từ thời điểm kết thúc ca tập."
                    )

        dispute = BookingDispute(
            booking_id=booking_id,
            sender_id=user.id,
            dispute_type=req.dispute_type,
            reason=req.reason or req.statement or "",
            evidence_url=req.evidence_url,
            status=DisputeStatus.PENDING,
            created_at=now_local(),
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

        # Quy chế trọng tài 48 giờ chống phán quyết độc đoán
        now = now_local()
        if not dispute.counter_argument:
            is_past_48h = dispute.deadline_at and now >= dispute.deadline_at
            if not is_past_48h and not req.force_override:
                raise BadRequestException(
                    "Theo quy chế trọng tài, cần chờ bên bị khiếu nại gửi bản phản biện đối chứng "
                    "hoặc hết thời hạn 48 giờ trước khi ban hành phán quyết. "
                    "Nếu cần phân xử khẩn cấp, vui lòng bật tùy chọn ghi đè giải trình (forceOverride)."
                )

        action = req.action.upper().strip()
        booking = dispute.booking
        if not booking:
            booking = self.booking_repo.get_by_id(dispute.booking_id)

        if action in ("REFUND_STUDENT", "RESOLVED_REFUND"):
            # Chấp thuận xử thắng cho Học viên: hoàn trả 1 buổi tập
            if booking and booking.enrollment_id:
                enrollment = booking.enrollment
                if enrollment:
                    enrollment.remaining_sessions += 1
                    enrollment.status = "ACTIVE"
            if booking and booking.attendance and booking.attendance.status == "ABSENT":
                booking.attendance.status = "PRESENT"

            dispute.status = DisputeStatus.RESOLVED_REFUND

        elif action in ("PAID_PT", "REJECTED"):
            # Xử thắng cho Huấn luyện viên: bác khiếu nại, giữ nguyên ca tập hoàn tất
            dispute.status = DisputeStatus.REJECTED

        elif action == "RESOLVED_FORCE_MAJEURE":
            # Hòa giải sự cố bất khả kháng: hoàn trả 1 buổi tập cho học viên, không phạt ai
            if booking and booking.enrollment_id:
                enrollment = booking.enrollment
                if enrollment:
                    enrollment.remaining_sessions += 1
                    enrollment.status = "ACTIVE"
            dispute.status = DisputeStatus.RESOLVED_REFUND

        elif action in ("CANCEL_CONTRACT_REFUND_STUDENT", "CONTRACT_TERMINATION"):
            # Thanh lý toàn bộ hợp đồng - Hoàn tiền các buổi chưa học cho học viên
            if booking and booking.enrollment:
                enroll = booking.enrollment
                rem_sessions = enroll.remaining_sessions
                if rem_sessions > 0 and enroll.total_sessions > 0:
                    refund_amount = (Decimal(str(enroll.final_price)) / Decimal(enroll.total_sessions)) * Decimal(rem_sessions)
                    student_wallet = self.wallet_repo.get_by_user_id(enroll.student_id)
                    if student_wallet:
                        student_wallet.balance += refund_amount
                        txn_ref = f"TXN_REFUND_CTR_{dispute.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        p_refund = Payment(
                            wallet_id=student_wallet.id,
                            enrollment_id=enroll.id,
                            amount=refund_amount,
                            payment_type=PaymentType.REFUND,
                            payment_method=PaymentMethod.WALLET,
                            status=PaymentStatus.SUCCESS,
                            transaction_ref=txn_ref,
                        )
                        self.db.add(p_refund)

                enroll.status = "CANCELLED"
                enroll.remaining_sessions = 0

                # Tự động hủy toàn bộ các ca tập tương lai chưa hoàn tất thuộc hợp đồng này để giải phóng khung giờ
                future_bookings = (
                    self.db.query(Booking)
                    .filter(
                        Booking.enrollment_id == enroll.id,
                        Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                    )
                    .all()
                )
                for fb in future_bookings:
                    fb.status = BookingStatus.CANCELLED
                    if fb.slot:
                        fb.slot.release()

            dispute.status = DisputeStatus.RESOLVED_REFUND

        elif action == "CANCEL_CONTRACT_PAID_PT":
            # Thanh lý toàn bộ hợp đồng - Thanh toán thù lao cho PT do học viên vi phạm nghiêm trọng
            if booking and booking.enrollment:
                enroll = booking.enrollment
                rem_sessions = enroll.remaining_sessions
                if rem_sessions > 0 and enroll.total_sessions > 0 and booking.pt and booking.pt.user_id:
                    total_remaining_val = (Decimal(str(enroll.final_price)) / Decimal(enroll.total_sessions)) * Decimal(rem_sessions)
                    pt_net = (total_remaining_val * Decimal("0.90")).quantize(Decimal("0.01"))
                    pt_wallet = self.wallet_repo.get_by_user_id(booking.pt.user_id)
                    if pt_wallet:
                        pt_wallet.balance += pt_net
                        txn_ref = f"TXN_EARN_CTR_{dispute.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        p_pt = Payment(
                            wallet_id=pt_wallet.id,
                            enrollment_id=enroll.id,
                            amount=pt_net,
                            payment_type=PaymentType.EARNING,
                            payment_method=PaymentMethod.WALLET,
                            status=PaymentStatus.SUCCESS,
                            transaction_ref=txn_ref,
                        )
                        self.db.add(p_pt)

                enroll.status = "CANCELLED"
                enroll.remaining_sessions = 0

                # Tự động hủy toàn bộ ca tập tương lai
                future_bookings = (
                    self.db.query(Booking)
                    .filter(
                        Booking.enrollment_id == enroll.id,
                        Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                    )
                    .all()
                )
                for fb in future_bookings:
                    fb.status = BookingStatus.CANCELLED
                    if fb.slot:
                        fb.slot.release()

            dispute.status = DisputeStatus.REJECTED

        else:
            raise BadRequestException(f"Hành động phân xử '{action}' không hợp lệ")

        dispute.admin_notes = req.admin_notes
        dispute.resolved_at = now_local()

        self.dispute_repo.update(dispute)
        self.db.commit()

        updated = self.dispute_repo.get_by_id(dispute.id)
        return self._to_response(updated)

    def submit_additional_evidence(
        self,
        dispute_id: int,
        user: User,
        req: SubmitAdditionalEvidenceRequest,
    ) -> DisputeResponse:
        dispute = self.dispute_repo.get_by_id_with_lock(dispute_id)
        if not dispute:
            raise ResourceNotFoundException(f"Không tìm thấy khiếu nại #{dispute_id}")

        booking = dispute.booking
        if not booking:
            booking = self.booking_repo.get_by_id(dispute.booking_id)

        is_student = (booking and booking.student_id == user.id)
        is_pt = bool(booking and booking.slot and booking.slot.pt and booking.slot.pt.user_id == user.id)

        if not is_student and not is_pt and user.role != Role.ADMIN:
            raise ForbiddenException("Bạn không phải bên liên quan trong vụ tranh chấp này")

        actor_tag = "Học viên bổ sung" if is_student else ("HLV bổ sung" if is_pt else "Admin ghi nhận")
        evidence_line = f"\n[{actor_tag}]: {req.evidence.strip()}"
        if dispute.counter_argument:
            dispute.counter_argument += evidence_line
        else:
            dispute.counter_argument = evidence_line.strip()

        self.dispute_repo.update(dispute)
        self.db.commit()

        updated = self.dispute_repo.get_by_id(dispute.id)
        return self._to_response(updated)

    def get_my_disputes(self, user: User) -> list[DisputeResponse]:
        disputes = self.dispute_repo.find_by_user_id(user.id)
        return [self._to_response(d) for d in disputes]

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
