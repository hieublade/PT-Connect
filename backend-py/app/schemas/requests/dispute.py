from pydantic import field_validator
from app.models.enums import DisputeType
from app.schemas.base import CamelModel


class CreateDisputeRequest(CamelModel):
    booking_id: int
    dispute_type: DisputeType = DisputeType.WRONG_ABSENT
    reason: str
    evidence_url: str | None = None

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        s = v.strip() if v else ""
        if len(s) < 5:
            raise ValueError("Lý do khiếu nại phải có ít nhất 5 ký tự")
        return s


class CounterDisputeRequest(CamelModel):
    counter_argument: str
    counter_evidence_url: str | None = None

    @field_validator("counter_argument")
    @classmethod
    def validate_argument(cls, v: str) -> str:
        s = v.strip() if v else ""
        if len(s) < 5:
            raise ValueError("Nội dung phản biện phải có ít nhất 5 ký tự")
        return s


class RequestEvidenceRequest(CamelModel):
    admin_notes: str

    @field_validator("admin_notes")
    @classmethod
    def validate_notes(cls, v: str) -> str:
        s = v.strip() if v else ""
        if not s:
            raise ValueError("Vui lòng ghi rõ nội dung bằng chứng cần bổ sung")
        return s


class ResolveDisputeRequest(CamelModel):
    action: str  # 'RESOLVED_REFUND', 'REJECTED', 'CONTRACT_TERMINATION'
    admin_notes: str

    @field_validator("admin_notes")
    @classmethod
    def validate_notes(cls, v: str) -> str:
        s = v.strip() if v else ""
        if len(s) < 5:
            raise ValueError("Lý do phán quyết của Quản trị viên bắt buộc và phải có ít nhất 5 ký tự")
        return s

