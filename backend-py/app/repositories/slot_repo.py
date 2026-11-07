from datetime import datetime

from sqlalchemy.orm import Session, selectinload

from app.models.availability_slot import AvailabilitySlot
from app.models.enums import SlotStatus
from app.models.pt_profile import PTProfile


class AvailabilitySlotRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, slot_id: int) -> AvailabilitySlot | None:
        return (
            self.db.query(AvailabilitySlot)
            .options(selectinload(AvailabilitySlot.pt).selectinload(PTProfile.pt))
            .filter(AvailabilitySlot.id == slot_id)
            .first()
        )

    def get_by_id_with_lock(self, slot_id: int) -> AvailabilitySlot | None:
        return (
            self.db.query(AvailabilitySlot)
            .options(selectinload(AvailabilitySlot.pt).selectinload(PTProfile.pt))
            .filter(AvailabilitySlot.id == slot_id)
            .with_for_update()
            .first()
        )

    def find_by_pt_id(self, pt_id: int) -> list[AvailabilitySlot]:
        return (
            self.db.query(AvailabilitySlot)
            .options(selectinload(AvailabilitySlot.pt).selectinload(PTProfile.pt))
            .filter(AvailabilitySlot.pt_id == pt_id)
            .order_by(AvailabilitySlot.start_time.asc())
            .all()
        )

    def find_available_slots_after(self, pt_id: int, after: datetime) -> list[AvailabilitySlot]:
        return (
            self.db.query(AvailabilitySlot)
            .options(selectinload(AvailabilitySlot.pt).selectinload(PTProfile.pt))
            .filter(
                AvailabilitySlot.pt_id == pt_id,
                AvailabilitySlot.status == SlotStatus.AVAILABLE,
                AvailabilitySlot.start_time > after,
            )
            .order_by(AvailabilitySlot.start_time.asc())
            .all()
        )

    def find_overlapping(
        self,
        pt_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_id: int | None = None,
    ) -> list[AvailabilitySlot]:
        query = self.db.query(AvailabilitySlot).filter(
            AvailabilitySlot.pt_id == pt_id,
            AvailabilitySlot.start_time < end_time,
            AvailabilitySlot.end_time > start_time,
        )
        if exclude_id is not None:
            query = query.filter(AvailabilitySlot.id != exclude_id)
        return query.all()

    def save(self, slot: AvailabilitySlot) -> AvailabilitySlot:
        self.db.add(slot)
        self.db.flush()
        return slot

    def delete(self, slot: AvailabilitySlot) -> None:
        self.db.delete(slot)
        self.db.flush()
