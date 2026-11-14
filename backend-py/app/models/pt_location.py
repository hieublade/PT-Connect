import unicodedata
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.pt_profile import PTProfile


def normalize_location_key(name: str) -> str:
    """Khóa so trùng địa điểm, mô phỏng collation utf8mb4_*_ci của MySQL:
    không phân biệt hoa/thường, không phân biệt dấu, gộp khoảng trắng."""
    text = unicodedata.normalize("NFD", name.replace("đ", "d").replace("Đ", "D"))
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return " ".join(text.casefold().split())


class PTLocation(Base):
    __tablename__ = "pt_locations"
    __table_args__ = (UniqueConstraint("pt_id", "location_name", name="uq_pt_location"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pt_id: Mapped[int] = mapped_column(ForeignKey("pt_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    location_name: Mapped[str] = mapped_column(String(255), nullable=False)

    profile: Mapped["PTProfile"] = relationship("PTProfile", back_populates="locations")

    def __init__(self, **kw):
        loc = kw.get("location_name", "")
        if isinstance(loc, str):
            kw["location_name"] = loc.strip()
        super().__init__(**kw)

    @property
    def match_key(self) -> str:
        return normalize_location_key(self.location_name or "")

    def __repr__(self) -> str:
        return f"<PTLocation(id={self.id}, pt_id={self.pt_id}, location_name='{self.location_name}')>"
