from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import FetchedValue, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from app.db.base import Base
from app.models.enums import VerificationStatus
from app.models.pt_location import PTLocation, normalize_location_key

if TYPE_CHECKING:
    from app.models.availability_slot import AvailabilitySlot
    from app.models.course import Course
    from app.models.user import PT


class PTProfile(Base):
    __tablename__ = "pt_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    specialty: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Bí danh tương thích ngược: code cũ đọc/ghi profile.specialties vẫn chạy
    specialties = synonym("specialty")
    experience_years: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    location_pricing_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    certificate_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    demo_video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Bí danh tương thích ngược: code cũ đọc/ghi profile.certificate_urls vẫn chạy
    certificate_urls = synonym("certificate_url")

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
    locations: Mapped[list["PTLocation"]] = relationship(
        "PTLocation",
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="PTLocation.id",
    )

    def __init__(self, **kw: Any):
        kw.setdefault("experience_years", 0)
        kw.setdefault("verification_status", VerificationStatus.PENDING)
        self._average_rating = Decimal(str(kw.pop("average_rating", "0.00")))
        self._total_reviews = int(kw.pop("total_reviews", 0))
        locs = kw.pop("available_locations", None)
        super().__init__(**kw)
        if locs is not None:
            self.replace_locations(locs)

    @property
    def average_rating(self) -> Decimal:
        """Thuộc tính dẫn xuất tính động (Chuẩn BCNF - không lưu cột vật lý)."""
        if hasattr(self, "_average_rating") and self._average_rating is not None:
            return Decimal(str(self._average_rating))
        ratings = []
        if getattr(self, "slots", None):
            for s in self.slots:
                for b in getattr(s, "bookings", []):
                    r = getattr(b, "review", None)
                    if r and getattr(r, "rating", None) is not None:
                        ratings.append(r.rating)
        if ratings:
            return Decimal(str(round(sum(ratings) / len(ratings), 2)))
        return Decimal("0.00")

    @average_rating.setter
    def average_rating(self, val: Any) -> None:
        self._average_rating = Decimal(str(val)) if val is not None else Decimal("0.00")

    @property
    def total_reviews(self) -> int:
        """Thuộc tính dẫn xuất tính động (Chuẩn BCNF - không lưu cột vật lý)."""
        if hasattr(self, "_total_reviews") and self._total_reviews is not None:
            return int(self._total_reviews)
        count = 0
        if getattr(self, "slots", None):
            for s in self.slots:
                for b in getattr(s, "bookings", []):
                    if getattr(b, "review", None) is not None:
                        count += 1
        return count

    @total_reviews.setter
    def total_reviews(self, val: Any) -> None:
        self._total_reviews = int(val) if val is not None else 0

    @property
    def available_locations(self) -> str:
        """Chuỗi địa điểm nối bằng '; ' tương thích ngược chuẩn API và views."""
        if not self.locations:
            return ""
        return "; ".join(loc.location_name for loc in self.locations if loc.location_name)

    @available_locations.setter
    def available_locations(self, value: str | list[str] | None) -> None:
        self.replace_locations(value)

    @property
    def location_names(self) -> list[str]:
        return [loc.location_name for loc in self.locations if loc.location_name]

    def has_location(self, name: str) -> bool:
        key = normalize_location_key(name or "")
        return bool(key) and any(loc.match_key == key for loc in self.locations)

    def add_location(self, name: str) -> None:
        """Thêm một địa điểm; bỏ qua tên rỗng hoặc trùng (không phân biệt hoa/thường, dấu)."""
        clean = " ".join(name.split()) if isinstance(name, str) else ""
        if not clean or self.has_location(clean):
            return
        self.locations.append(PTLocation(location_name=clean))

    def replace_locations(self, locations_input: str | list[str] | None) -> None:
        """Cập nhật theo khác biệt: giữ nguyên dòng đã có, chỉ xóa dòng bị bỏ và thêm dòng mới.

        Không dùng clear() rồi thêm lại, vì SQLAlchemy flush INSERT trước DELETE
        sẽ làm dòng mới đụng UNIQUE `uq_pt_location` với chính dòng cũ chưa bị xóa.
        """
        desired: dict[str, str] = {}
        for name in self._parse_locations(locations_input):
            desired.setdefault(normalize_location_key(name), name)

        kept: dict[str, PTLocation] = {}
        for loc in list(self.locations):
            key = loc.match_key
            if key in desired and key not in kept:
                kept[key] = loc
            else:
                self.locations.remove(loc)

        for key, name in desired.items():
            loc = kept.get(key)
            if loc is None:
                self.locations.append(PTLocation(location_name=name))
            elif loc.location_name != name:
                loc.location_name = name

    @staticmethod
    def _parse_locations(locations_input: str | list[str] | None) -> list[str]:
        if not locations_input:
            return []
        raw = locations_input.split(";") if isinstance(locations_input, str) else [str(p) for p in locations_input]
        return [" ".join(p.split()) for p in raw if p and p.strip()]

    def approve(self) -> None:
        self.verification_status = VerificationStatus.VERIFIED
        if self.pt is not None:
            self.pt.activate()

    def reject(self) -> None:
        self.verification_status = VerificationStatus.REJECTED
        if self.pt is not None:
            self.pt.suspend()
