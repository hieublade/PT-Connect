from sqlalchemy.orm import Session

from app.models.enums import Role, UserStatus, VerificationStatus
from app.models.pt_profile import PTProfile
from app.models.user import PT, User
from app.schemas.requests.auth import RegisterRequest


class PtRegistrationHandler:
    def supports(self, role: Role) -> bool:
        return role == Role.PT

    def register(self, db: Session, request: RegisterRequest, password_hash: str) -> User:
        pt = PT(
            full_name=request.full_name,
            email=request.email,
            password_hash=password_hash,
            phone=request.phone,
            role=Role.PT,
            status=UserStatus.PENDING,
        )
        db.add(pt)
        db.flush()

        locations = (
            request.available_locations.strip()
            if request.available_locations and request.available_locations.strip()
            else "Chưa cập nhật địa điểm"
        )

        profile = PTProfile(
            pt=pt,
            bio=request.bio,
            experience_years=request.experience_years if request.experience_years is not None else 0,
            available_locations=locations,
            location_pricing_note=request.location_pricing_note,
            certificate_url=request.clean_certificate_url,
            verification_status=VerificationStatus.PENDING,
        )
        db.add(profile)
        db.flush()
        pt.profile = profile
        return pt
