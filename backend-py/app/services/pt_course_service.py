from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundException, UnauthorizedException
from app.models.course import Course
from app.models.enums import CourseStatus
from app.repositories.course_repo import CourseRepository
from app.repositories.enrollment_repo import EnrollmentRepository
from app.schemas.requests.pt import CreateCourseRequest, UpdateCourseRequest
from app.schemas.responses.pt import CourseResponse
from app.services.pt_profile_service import PTProfileService


class PTCourseService:
    def __init__(self, db: Session):
        self.db = db
        self.profile_service = PTProfileService(db)
        self.course_repo = CourseRepository(db)
        self.enrollment_repo = EnrollmentRepository(db)

    def create_course(self, user_email: str, request: CreateCourseRequest) -> CourseResponse:
        profile = self.profile_service.get_pt_profile_entity(user_email)

        course = Course(
            pt_id=profile.id,
            title=request.title.strip(),
            description=request.description,
            total_sessions=request.total_sessions,
            validity_days=request.validity_days,
            base_price=request.base_price,
            status=CourseStatus.ACTIVE,
        )
        saved = self.course_repo.save(course)
        self.db.commit()
        self.db.refresh(saved)
        return CourseResponse.from_entity(saved)

    def get_courses(self, user_email: str) -> list[CourseResponse]:
        profile = self.profile_service.get_pt_profile_entity(user_email)
        courses = self.course_repo.find_by_pt_id(profile.id)
        return [CourseResponse.from_entity(c) for c in courses if c]

    def update_course(self, user_email: str, course_id: int, request: UpdateCourseRequest) -> CourseResponse:
        profile = self.profile_service.get_pt_profile_entity(user_email)
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise ResourceNotFoundException(f"Không tìm thấy khóa học với ID: {course_id}")

        if course.pt_id != profile.id:
            raise UnauthorizedException("Bạn không có quyền chỉnh sửa khóa học của Huấn luyện viên khác")

        course.title = request.title.strip()
        course.description = request.description
        course.total_sessions = request.total_sessions
        course.validity_days = request.validity_days
        course.base_price = request.base_price
        if request.status is not None:
            course.status = request.status

        saved = self.course_repo.save(course)
        self.db.commit()
        self.db.refresh(saved)
        return CourseResponse.from_entity(saved)

    def delete_course(self, user_email: str, course_id: int) -> None:
        profile = self.profile_service.get_pt_profile_entity(user_email)
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise ResourceNotFoundException(f"Không tìm thấy khóa học với ID: {course_id}")

        if course.pt_id != profile.id:
            raise UnauthorizedException("Bạn không có quyền xóa khóa học của Huấn luyện viên khác")

        if self.enrollment_repo.find_by_course_id(course_id):
            raise ValueError(
                "Khóa học đã có hợp đồng học viên đăng ký, chỉ có thể ngưng bán (chuyển sang INACTIVE)"
            )

        self.course_repo.delete(course)
        self.db.commit()
