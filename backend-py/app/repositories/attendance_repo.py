from sqlalchemy.orm import Session, selectinload

from app.models.attendance import Attendance


class AttendanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, attendance_id: int) -> Attendance | None:
        return (
            self.db.query(Attendance)
            .options(selectinload(Attendance.booking))
            .filter(Attendance.id == attendance_id)
            .first()
        )

    def get_by_booking_id(self, booking_id: int) -> Attendance | None:
        return (
            self.db.query(Attendance)
            .options(selectinload(Attendance.booking))
            .filter(Attendance.booking_id == booking_id)
            .first()
        )

    def save(self, attendance: Attendance) -> Attendance:
        self.db.add(attendance)
        self.db.flush()
        return attendance
