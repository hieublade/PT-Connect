from sqlalchemy.orm import Session

from app.core.clock import now_local
from app.core.exceptions import ResourceNotFoundException, UnauthorizedException
from app.models.availability_slot import AvailabilitySlot
from app.models.enums import SlotStatus
from app.repositories.booking_repo import BookingRepository
from app.repositories.slot_repo import AvailabilitySlotRepository
from app.schemas.requests.pt import CreateSlotRequest
from app.schemas.responses.pt import SlotResponse
from app.services.pt_profile_service import PTProfileService


class PTSlotService:
    def __init__(self, db: Session):
        self.db = db
        self.profile_service = PTProfileService(db)
        self.slot_repo = AvailabilitySlotRepository(db)
        self.booking_repo = BookingRepository(db)

    def create_slot(self, user_email: str, request: CreateSlotRequest) -> SlotResponse:
        profile = self.profile_service.get_pt_profile_entity(user_email)

        if not request.start_time or not request.end_time:
            raise ValueError("Thời gian bắt đầu và kết thúc không được để trống")

        now = now_local()
        if request.start_time < now:
            raise ValueError("Thời gian bắt đầu slot không được ở trong quá khứ")

        if not request.end_time > request.start_time:
            raise ValueError("Thời gian kết thúc slot phải sau thời gian bắt đầu")

        overlapping = self.slot_repo.find_overlapping(
            profile.id, request.start_time, request.end_time, None
        )
        if overlapping:
            raise ValueError("Khung giờ bị trùng hoặc chồng lấn với lịch rảnh khác của bạn")

        slot = AvailabilitySlot(
            pt_id=profile.id,
            start_time=request.start_time,
            end_time=request.end_time,
            status=SlotStatus.AVAILABLE,
        )
        saved = self.slot_repo.save(slot)
        self.db.commit()
        self.db.refresh(saved)
        return SlotResponse.from_entity(saved)

    def get_slots(self, user_email: str) -> list[SlotResponse]:
        profile = self.profile_service.get_pt_profile_entity(user_email)
        slots = self.slot_repo.find_by_pt_id(profile.id)
        return [SlotResponse.from_entity(s) for s in slots if s]

    def delete_slot(self, user_email: str, slot_id: int) -> None:
        profile = self.profile_service.get_pt_profile_entity(user_email)
        slot = self.slot_repo.get_by_id(slot_id)
        if not slot:
            raise ResourceNotFoundException(f"Không tìm thấy khung giờ (slot) với ID: {slot_id}")

        if slot.pt_id != profile.id:
            raise UnauthorizedException("Bạn không có quyền xóa khung giờ của Huấn luyện viên khác")

        if self.booking_repo.find_by_slot_id(slot_id) is not None:
            raise ValueError("Không thể xóa khung giờ đã có học viên đặt lịch")

        if slot.status != SlotStatus.AVAILABLE:
            raise ValueError("Chỉ có thể xóa khung giờ đang ở trạng thái AVAILABLE")

        self.slot_repo.delete(slot)
        self.db.commit()
