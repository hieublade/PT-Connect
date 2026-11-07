from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import FetchedValue, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CourseStatus

if TYPE_CHECKING:
    from app.models.enrollment import Enrollment
    from app.models.pt_profile import PTProfile


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pt_id: Mapped[int] = mapped_column(ForeignKey("pt_profiles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_sessions: Mapped[int] = mapped_column(Integer, nullable=False)
    validity_days: Mapped[int] = mapped_column(Integer, nullable=False)
    base_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[CourseStatus] = mapped_column(
        SQLEnum(CourseStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=CourseStatus.ACTIVE,
    )
    created_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())

    pt: Mapped["PTProfile"] = relationship("PTProfile", back_populates="courses")
    enrollments: Mapped[list["Enrollment"]] = relationship("Enrollment", back_populates="course")
