from app.models.enums import DisputeType, DisputeStatus
from app.schemas.base import CamelModel, LocalDateTime


class DisputeResponse(CamelModel):
    id: int
    booking_id: int
    sender_id: int
    sender_role: str
    sender_name: str | None = None
    dispute_type: DisputeType
    reason: str
    evidence_url: str | None = None
    counter_evidence_url: str | None = None
    counter_argument: str | None = None
    status: DisputeStatus
    admin_notes: str | None = None
    deadline_at: LocalDateTime | None = None
    resolved_at: LocalDateTime | None = None
    created_at: LocalDateTime | None = None

    # Booking & parties context
    student_id: int | None = None
    student_name: str | None = None
    pt_id: int | None = None
    pt_name: str | None = None
    start_time: LocalDateTime | None = None
    end_time: LocalDateTime | None = None

