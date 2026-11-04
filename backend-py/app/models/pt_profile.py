from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import FetchedValue, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from app.db.base import Base
from app.models.enums import VerificationStatus

if TYPE_CHECKING:
    from app.models.availability_slot import AvailabilitySlot
    from app.models.course import Course
    from app.models.user import PT


class PTProfile(Base):
    __tablename__ = "pt_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    experience_years: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    available_locations: Mapped[str] = mapped_column(Text, nullable=False)
    location_pricing_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    certificate_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Bí danh tương thích ngược: code cũ đọc/ghi profile.certificate_urls vẫn chạy,
    # và PTProfile(certificate_urls=...) vẫn hợp lệ. Cả hai trỏ vào cùng cột certificate_url.
    certificate_urls = synonym("certificate_url")

    average_rating: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        nullable=False,
        server_default=FetchedValue(),
    )
    total_reviews: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=FetchedValue(),
    )
    verification_status: Mapped[VerificationStatus] = mapped_column(
        SQLEnum(VerificationStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=VerificationStatus.PENDING,
    )
    created_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())
    updated_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())

    pt: Mapped["PT"] = relationship("PT", back_populates="profile", foreign_keys=[user_id])
    courses: Mapped[list["Course"]] = relationship("Course", back_populates="pt")
    slots: Mapped[list["AvailabilitySlot"]] = relationship("AvailabilitySlot", back_populates="pt")

    def __init__(self, **kw):
        kw.setdefault("experience_years", 0)
        kw.setdefault("verification_status", VerificationStatus.PENDING)
        kw.setdefault("average_rating", Decimal("0.00"))
        kw.setdefault("total_reviews", 0)
        super().__init__(**kw)

    def approve(self) -> None:
        self.verification_status = VerificationStatus.VERIFIED
        if self.pt is not None:
            self.pt.activate()

    def reject(self) -> None:
        self.verification_status = VerificationStatus.REJECTED
        if self.pt is not None:
            self.pt.pending()
