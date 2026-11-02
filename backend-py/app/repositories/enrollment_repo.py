from sqlalchemy.orm import Session, selectinload

from app.models.enrollment import Enrollment
from app.models.enums import EnrollmentStatus
from app.models.pt_profile import PTProfile


class EnrollmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, enrollment_id: int) -> Enrollment | None:
        return (
            self.db.query(Enrollment)
            .options(
                selectinload(Enrollment.student),
                selectinload(Enrollment.course),
                selectinload(Enrollment.pt).selectinload(PTProfile.pt),
            )
            .filter(Enrollment.id == enrollment_id)
            .first()
        )

    def get_by_id_with_lock(self, enrollment_id: int) -> Enrollment | None:
        return (
            self.db.query(Enrollment)
            .options(
                selectinload(Enrollment.student),
                selectinload(Enrollment.course),
                selectinload(Enrollment.pt).selectinload(PTProfile.pt),
            )
            .filter(Enrollment.id == enrollment_id)
            .with_for_update()
            .first()
        )

    def find_by_student_id(self, student_id: int) -> list[Enrollment]:
        return (
            self.db.query(Enrollment)
            .options(
                selectinload(Enrollment.student),
                selectinload(Enrollment.course),
                selectinload(Enrollment.pt).selectinload(PTProfile.pt),
            )
            .filter(Enrollment.student_id == student_id)
            .order_by(Enrollment.created_at.desc())
            .all()
        )

    def find_by_pt_id(self, pt_id: int) -> list[Enrollment]:
        return (
            self.db.query(Enrollment)
            .options(
                selectinload(Enrollment.student),
                selectinload(Enrollment.course),
                selectinload(Enrollment.pt).selectinload(PTProfile.pt),
            )
            .filter(Enrollment.pt_id == pt_id)
            .order_by(Enrollment.created_at.desc())
            .all()
        )

    def find_by_course_id(self, course_id: int) -> list[Enrollment]:
        return self.db.query(Enrollment).filter(Enrollment.course_id == course_id).all()

    def find_active_by_student_and_course(self, student_id: int, course_id: int) -> list[Enrollment]:
        return (
            self.db.query(Enrollment)
            .filter(
                Enrollment.student_id == student_id,
                Enrollment.course_id == course_id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
                Enrollment.remaining_sessions > 0,
            )
            .all()
        )

    def save(self, enrollment: Enrollment) -> Enrollment:
        self.db.add(enrollment)
        self.db.flush()
        return enrollment
