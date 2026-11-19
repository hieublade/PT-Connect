from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.clock import now_local
from app.core.exceptions import ResourceNotFoundException, UnauthorizedException
from app.models.enums import CourseStatus, Role, UserStatus
from app.models.pt_profile import PTProfile
from app.repositories.course_repo import CourseRepository
from app.repositories.pt_profile_repo import PTProfileRepository
from app.repositories.slot_repo import AvailabilitySlotRepository
from app.repositories.user_repo import UserRepository
from app.schemas.requests.pt import UpdatePTProfileRequest
from app.schemas.responses.pt import CourseResponse, PTProfileResponse, PTPublicDTO, SlotResponse


class PTProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.profile_repo = PTProfileRepository(db)
        self.course_repo = CourseRepository(db)
        self.slot_repo = AvailabilitySlotRepository(db)

    def get_pt_profile_entity(self, user_email: str) -> PTProfile:
        user = self.user_repo.get_by_email(user_email)
        if not user:
            raise ResourceNotFoundException("Không tìm thấy thông tin người dùng")

        if user.role != Role.PT:
            raise UnauthorizedException("Tài khoản của bạn không có vai trò Huấn luyện viên")

        if user.status == UserStatus.SUSPENDED:
            raise UnauthorizedException("Tài khoản Huấn luyện viên hiện đang bị khóa")

        profile = self.profile_repo.get_by_user_id(user.id)
        if not profile:
            raise ResourceNotFoundException("Chưa tìm thấy hồ sơ Huấn luyện viên cho tài khoản này")

        return profile

    def _populate_rating_stats(self, profiles: list[PTProfile]) -> None:
        """Gắn trước điểm đánh giá từ View v_pt_rating_statistics trong 1 truy vấn duy nhất (tránh N+1 query)."""
        if not profiles:
            return
        try:
            stats = self.db.execute(text("SELECT pt_profile_id, average_rating, total_reviews FROM v_pt_rating_statistics")).fetchall()
            stats_map = {row[0]: (row[1], row[2]) for row in stats}
            for p in profiles:
                if p.id in stats_map:
                    p._average_rating = stats_map[p.id][0]
                    p._total_reviews = stats_map[p.id][1]
                else:
                    p._average_rating = Decimal("0.00")
                    p._total_reviews = 0
        except Exception:
            pass

    def get_public_pt_profiles(self, name: str | None = None) -> list[PTPublicDTO]:
        profiles = self.profile_repo.search_verified_pts(name)
        self._populate_rating_stats(profiles)
        result = []
        for profile in profiles:
            if profile.pt and profile.pt.status == UserStatus.ACTIVE:
                result.append(self._map_to_public_dto(profile))
        return result

    def get_public_pt_profile_by_id(self, profile_id: int) -> PTPublicDTO:
        profile = self.profile_repo.get_by_id(profile_id)
        if not profile:
            raise ResourceNotFoundException(f"Không tìm thấy hồ sơ Huấn luyện viên với ID: {profile_id}")
        self._populate_rating_stats([profile])
        return self._map_to_public_dto(profile)

    def get_active_courses_by_pt_profile_id(self, profile_id: int) -> list[CourseResponse]:
        profile = self.profile_repo.get_by_id(profile_id)
        if not profile:
            raise ResourceNotFoundException(f"Không tìm thấy hồ sơ Huấn luyện viên với ID: {profile_id}")

        courses = self.course_repo.find_by_pt_id_and_status(profile_id, CourseStatus.ACTIVE)
        return [CourseResponse.from_entity(c) for c in courses if c]

    def get_available_slots_by_pt_profile_id(self, profile_id: int) -> list[SlotResponse]:
        profile = self.profile_repo.get_by_id(profile_id)
        if not profile:
            raise ResourceNotFoundException(f"Không tìm thấy hồ sơ Huấn luyện viên với ID: {profile_id}")

        slots = self.slot_repo.find_available_slots_after(profile_id, now_local())
        return [SlotResponse.from_entity(s) for s in slots if s]

    def get_profile(self, user_email: str) -> PTProfileResponse:
        profile = self.get_pt_profile_entity(user_email)
        return PTProfileResponse.from_entity(profile)

    def update_profile(self, user_email: str, request: UpdatePTProfileRequest) -> PTProfileResponse:
        profile = self.get_pt_profile_entity(user_email)

        profile.bio = request.bio
        profile.experience_years = request.experience_years if request.experience_years is not None else 0
        profile.available_locations = request.available_locations
        profile.location_pricing_note = request.location_pricing_note
        if request.clean_certificate_url is not None:
            profile.certificate_url = request.clean_certificate_url

        self.db.commit()
        self.db.refresh(profile)
        return PTProfileResponse.from_entity(profile)

    def _map_to_public_dto(self, profile: PTProfile) -> PTPublicDTO:
        if getattr(profile, "courses", None) is not None:
            active_courses = [c for c in profile.courses if c.status == CourseStatus.ACTIVE]
        else:
            active_courses = self.course_repo.find_by_pt_id_and_status(profile.id, CourseStatus.ACTIVE)
        valid_prices = [c.base_price for c in active_courses if c.base_price and c.base_price > Decimal(0)]
        lowest_price = min(valid_prices) if valid_prices else None
        return PTPublicDTO.from_entity(profile, lowest_price=lowest_price)
