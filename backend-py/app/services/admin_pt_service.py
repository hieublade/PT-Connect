from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundException
from app.repositories.pt_profile_repo import PTProfileRepository
from app.repositories.user_repo import UserRepository
from app.schemas.responses.pt import PendingPTResponse, PTProfileResponse


class AdminPTService:
    def __init__(self, db: Session):
        self.db = db
        self.profile_repo = PTProfileRepository(db)
        self.user_repo = UserRepository(db)

    def get_pending_pts(self) -> list[PendingPTResponse]:
        profiles = self.profile_repo.get_pending_profiles()
        return [PendingPTResponse.from_entity(p) for p in profiles if p]

    def approve_pt(self, pt_profile_id: int) -> PTProfileResponse:
        profile = self.profile_repo.get_by_id(pt_profile_id)
        if not profile:
            raise ResourceNotFoundException(f"Không tìm thấy hồ sơ PT với ID: {pt_profile_id}")

        profile.approve()
        if profile.pt is not None:
            self.user_repo.save(profile.pt)

        saved = self.profile_repo.save(profile)
        self.db.commit()
        self.db.refresh(saved)
        return PTProfileResponse.from_entity(saved)

    def reject_pt(self, pt_profile_id: int) -> PTProfileResponse:
        profile = self.profile_repo.get_by_id(pt_profile_id)
        if not profile:
            raise ResourceNotFoundException(f"Không tìm thấy hồ sơ PT với ID: {pt_profile_id}")

        profile.reject()
        if profile.pt is not None:
            self.user_repo.save(profile.pt)

        saved = self.profile_repo.save(profile)
        self.db.commit()
        self.db.refresh(saved)
        return PTProfileResponse.from_entity(saved)
