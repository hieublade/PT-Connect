import logging
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.clock import today_local
from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    ResourceNotFoundException,
    UnauthorizedException,
)
from app.models.enrollment import Enrollment
from app.models.enums import CourseStatus, EnrollmentStatus, Role
from app.models.user import User
from app.pdf.contract import contract_pdf_generator
from app.repositories.course_repo import CourseRepository
from app.repositories.enrollment_repo import EnrollmentRepository
from app.repositories.payment_repo import PaymentRepository
from app.repositories.pt_profile_repo import PTProfileRepository
from app.repositories.user_repo import UserRepository
from app.schemas.requests.enrollment import PurchaseCourseRequest
from app.schemas.responses.enrollment import EnrollmentResponse
from app.services.wallet_service import WalletService

logger = logging.getLogger(__name__)


class EnrollmentService:
    def __init__(self, db: Session):
        self.db = db
        self.enrollment_repo = EnrollmentRepository(db)
        self.course_repo = CourseRepository(db)
        self.user_repo = UserRepository(db)
        self.pt_profile_repo = PTProfileRepository(db)
        self.payment_repo = PaymentRepository(db)
        self.wallet_service = WalletService(db)

    def purchase_course(self, student_email: str, request: PurchaseCourseRequest) -> EnrollmentResponse:
        student = self.user_repo.get_by_email(student_email)
        if not student:
            raise ResourceNotFoundException(f"Không tìm thấy học viên với email: {student_email}")

        course = self.course_repo.get_by_id(request.course_id)
        if not course:
            raise ResourceNotFoundException(f"Không tìm thấy khóa học với ID: {request.course_id}")

        if course.status != CourseStatus.ACTIVE:
            raise BadRequestException("Khóa học hiện không còn mở bán")

        # Check existing active enrollment for same course with remaining sessions
        active_enrollments = self.enrollment_repo.find_active_by_student_and_course(student.id, course.id)
        if active_enrollments:
            active_enr = active_enrollments[0]
            rem = active_enr.remaining_sessions
            tot = active_enr.total_sessions
            raise BadRequestException(
                f"Bạn đang có một hợp đồng cho khóa học này còn hiệu lực (còn {rem}/{tot} buổi chưa hoàn thành). "
                "Vui lòng hoàn thành toàn bộ buổi tập trước khi đăng ký tiếp!"
            )

        if not request.training_location or not request.training_location.strip():
            raise BadRequestException("Địa điểm tập luyện cố định không được để trống")

        start_date = today_local()
        end_date = start_date + timedelta(days=course.validity_days)

        enrollment = Enrollment(
            student_id=student.id,
            course_id=course.id,
            training_location=request.training_location.strip(),
            final_price=course.base_price,
            total_sessions=course.total_sessions,
            remaining_sessions=course.total_sessions,
            start_date=start_date,
            end_date=end_date,
            contract_url="/api/v1/enrollments/contract-generating",
            status=EnrollmentStatus.ACTIVE,
        )
        saved = self.enrollment_repo.save(enrollment)

        payment = self.wallet_service.process_course_purchase(
            user_id=student.id,
            enrollment=saved,
            amount=course.base_price,
            payment_method=request.payment_method,
        )

        saved.contract_url = f"/api/v1/enrollments/{saved.id}/contract"
        self.enrollment_repo.save(saved)
        self.db.commit()
        self.db.refresh(saved)

        # Generate contract PDF
        try:
            contract_pdf_generator.generate_contract_pdf(saved, payment.transaction_ref)
        except Exception as e:
            logger.warning("Không thể sinh file PDF hợp đồng: %s", e)

        return EnrollmentResponse.from_entity(saved)

    def get_my_enrollments(self, student_email: str) -> list[EnrollmentResponse]:
        student = self.user_repo.get_by_email(student_email)
        if not student:
            raise ResourceNotFoundException(f"Không tìm thấy học viên với email: {student_email}")

        enrollments = self.enrollment_repo.find_by_student_id(student.id)
        return [EnrollmentResponse.from_entity(e) for e in enrollments if e]

    def get_enrollment_by_id(self, user_email: str, enrollment_id: int) -> EnrollmentResponse:
        user = self.user_repo.get_by_email(user_email)
        if not user:
            raise ResourceNotFoundException(f"Không tìm thấy người dùng với email: {user_email}")

        enrollment = self.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment:
            raise ResourceNotFoundException(f"Không tìm thấy hợp đồng với ID: {enrollment_id}")

        self._validate_access(user, enrollment)
        return EnrollmentResponse.from_entity(enrollment)

    def get_contract_pdf(self, user_email: str, enrollment_id: int) -> bytes:
        user = self.user_repo.get_by_email(user_email)
        if not user:
            raise ResourceNotFoundException(f"Không tìm thấy người dùng với email: {user_email}")

        enrollment = self.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment:
            raise ResourceNotFoundException(f"Không tìm thấy hợp đồng với ID: {enrollment_id}")

        self._validate_access(user, enrollment)

        pdf_bytes = contract_pdf_generator.get_existing_contract_pdf(enrollment_id)
        if pdf_bytes is None:
            # Look up txn_ref from payments
            txn_ref = None
            payments = (
                self.db.query(self.payment_repo.get_by_id.__annotations__.get("return", None))
                if False
                else self.payment_repo.find_by_wallet_id(user.wallet.id if user.wallet else 0)
            )
            for p in payments:
                if p.enrollment_id == enrollment_id:
                    txn_ref = p.transaction_ref
                    break
            pdf_bytes = contract_pdf_generator.generate_contract_pdf(enrollment, txn_ref)

        return pdf_bytes

    def get_pt_enrollments(self, pt_email: str) -> list[EnrollmentResponse]:
        user = self.user_repo.get_by_email(pt_email)
        if not user or user.role != Role.PT:
            raise UnauthorizedException("Chỉ Huấn luyện viên mới có quyền xem danh sách hợp đồng")

        pt_profile = self.pt_profile_repo.get_by_user_id(user.id)
        if not pt_profile:
            raise UnauthorizedException("Chỉ Huấn luyện viên mới có quyền xem danh sách hợp đồng")

        enrollments = self.enrollment_repo.find_by_pt_id(pt_profile.id)
        return [EnrollmentResponse.from_entity(e) for e in enrollments if e]

    def _validate_access(self, user: User, enrollment: Enrollment) -> None:
        if user.role == Role.ADMIN:
            return

        if user.role == Role.STUDENT and enrollment.student_id == user.id:
            return

        if user.role == Role.PT and enrollment.pt and enrollment.pt.user_id == user.id:
            return

        raise ForbiddenException("Bạn không có quyền truy cập hợp đồng này")
