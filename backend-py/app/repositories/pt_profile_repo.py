from sqlalchemy.orm import Session, selectinload

from app.models.enums import VerificationStatus
from app.models.pt_profile import PTProfile
from app.models.user import PT


class PTProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, profile_id: int) -> PTProfile | None:
        return (
            self.db.query(PTProfile)
            .options(
                selectinload(PTProfile.pt),
                selectinload(PTProfile.courses),
                selectinload(PTProfile.locations),
            )
            .filter(PTProfile.id == profile_id)
            .first()
        )

    def get_by_user_id(self, user_id: int) -> PTProfile | None:
        return (
            self.db.query(PTProfile)
            .options(
                selectinload(PTProfile.pt),
                selectinload(PTProfile.locations),
            )
            .filter(PTProfile.user_id == user_id)
            .first()
        )

    def get_by_email(self, email: str) -> PTProfile | None:
        return (
            self.db.query(PTProfile)
            .join(PTProfile.pt)
            .options(
                selectinload(PTProfile.pt),
                selectinload(PTProfile.courses),
                selectinload(PTProfile.locations),
            )
            .filter(PT.email == email)
            .first()
        )

    def get_pending_profiles(self) -> list[PTProfile]:
        return (
            self.db.query(PTProfile)
            .options(
                selectinload(PTProfile.pt),
                selectinload(PTProfile.locations),
            )
            .filter(PTProfile.verification_status == VerificationStatus.PENDING)
            .all()
        )

    def search_verified_pts(self, name: str | None = None) -> list[PTProfile]:
        query = (
            self.db.query(PTProfile)
            .join(PTProfile.pt)
            .options(
                selectinload(PTProfile.pt),
                selectinload(PTProfile.courses),
                selectinload(PTProfile.locations),
            )
            .filter(PTProfile.verification_status == VerificationStatus.VERIFIED)
        )
        if name and name.strip():
            search = f"%{name.strip()}%"
            query = query.filter(PT.full_name.ilike(search))
        return query.all()

    def save(self, profile: PTProfile) -> PTProfile:
        self.db.add(profile)
        self.db.flush()
        return profile
