from sqlalchemy.orm import Session, selectinload

from app.models.course import Course
from app.models.enums import CourseStatus
from app.models.pt_profile import PTProfile


class CourseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, course_id: int) -> Course | None:
        return (
            self.db.query(Course)
            .options(selectinload(Course.pt).selectinload(PTProfile.pt))
            .filter(Course.id == course_id)
            .first()
        )

    def find_by_pt_id(self, pt_id: int) -> list[Course]:
        return (
            self.db.query(Course)
            .options(selectinload(Course.pt).selectinload(PTProfile.pt))
            .filter(Course.pt_id == pt_id)
            .all()
        )

    def find_by_pt_id_and_status(self, pt_id: int, status: CourseStatus) -> list[Course]:
        return (
            self.db.query(Course)
            .options(selectinload(Course.pt).selectinload(PTProfile.pt))
            .filter(Course.pt_id == pt_id, Course.status == status)
            .all()
        )

    def save(self, course: Course) -> Course:
        self.db.add(course)
        self.db.flush()
        return course

    def delete(self, course: Course) -> None:
        self.db.delete(course)
        self.db.flush()
