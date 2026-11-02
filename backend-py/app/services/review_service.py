from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, ResourceNotFoundException
from app.models.enums import BookingStatus
from app.models.review import Review
from app.repositories.booking_repo import BookingRepository
from app.repositories.pt_profile_repo import PTProfileRepository
from app.repositories.review_repo import ReviewRepository
from app.repositories.user_repo import UserRepository
from app.schemas.requests.review import CreateReviewRequest
from app.schemas.responses.review import ReviewResponse


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.review_repo = ReviewRepository(db)
        self.booking_repo = BookingRepository(db)
        self.user_repo = UserRepository(db)
        self.pt_profile_repo = PTProfileRepository(db)

    def create_review(self, student_email: str, request: CreateReviewRequest) -> ReviewResponse:
        student = self.user_repo.get_by_email(student_email)
        if not student:
            raise ResourceNotFoundException(f"Không tìm thấy học viên với email: {student_email}")

        booking = self.booking_repo.get_by_id(request.booking_id)
        if not booking:
            raise ResourceNotFoundException(f"Không tìm thấy ca tập với ID: {request.booking_id}")

        if booking.student_id != student.id:
            raise BadRequestException("Bạn không có quyền đánh giá đơn đặt lịch của học viên khác")

        if booking.status != BookingStatus.COMPLETED:
            raise BadRequestException("Chỉ có thể đánh giá ca tập đã hoàn thành (COMPLETED)")

        if self.review_repo.find_by_booking_id(booking.id) is not None:
            raise BadRequestException(
                "Ca tập này đã được đánh giá trước đó. Mỗi ca tập chỉ được đánh giá 1 lần duy nhất!"
            )

        review = Review(
            booking_id=booking.id,
            student_id=student.id,
            pt_id=booking.pt_id,
            rating=request.rating,
            comment=request.comment.strip() if request.comment else None,
        )

        saved = self.review_repo.save(review)
        self.db.commit()
        self.db.refresh(saved)
        return ReviewResponse.from_entity(saved)

    def get_reviews_by_pt_id(self, pt_id: int) -> list[ReviewResponse]:
        profile = self.pt_profile_repo.get_by_id(pt_id)
        if not profile:
            raise ResourceNotFoundException(f"Không tìm thấy hồ sơ Huấn luyện viên với ID: {pt_id}")

        reviews = self.review_repo.find_by_pt_id(pt_id)
        return [ReviewResponse.from_entity(r) for r in reviews if r]

    def get_my_reviews(self, student_email: str) -> list[ReviewResponse]:
        student = self.user_repo.get_by_email(student_email)
        if not student:
            raise ResourceNotFoundException(f"Không tìm thấy học viên với email: {student_email}")

        reviews = self.review_repo.find_by_student_id(student.id)
        return [ReviewResponse.from_entity(r) for r in reviews if r]

    def get_review_by_booking_id(self, booking_id: int) -> ReviewResponse | None:
        review = self.review_repo.find_by_booking_id(booking_id)
        return ReviewResponse.from_entity(review)
