from pydantic import field_validator, model_validator
from app.models.enums import DisputeType
from app.schemas.base import CamelModel


class CreateDisputeRequest(CamelModel):
    booking_id: int | None = None
    enrollment_id: int | None = None
    dispute_type: str | DisputeType = DisputeType.WRONG_ABSENT
    dispute_type_label: str | None = None
    severity: str | None = "MEDIUM"
    reason: str | None = None
    statement: str | None = None
    evidence_url: str | None = None
    evidence_note: str | None = None

    @model_validator(mode="after")
    def _normalize_statement(self) -> "CreateDisputeRequest":
        if not self.reason and self.statement:
            self.reason = self.statement
        if not self.statement and self.reason:
            self.statement = self.reason
        if not self.reason or len(self.reason.strip()) < 5:
            raise ValueError("Lý do / tường trình khiếu nại phải có ít nhất 5 ký tự")
        self.reason = self.reason.strip()
        self.statement = self.reason

        if isinstance(self.dispute_type, str):
            dt_upper = self.dispute_type.upper().strip()
            # Map Java types to Python enum where helpful
            mapping = {
                "PT_ABSENT": DisputeType.PT_NO_SHOW,
                "LATE_CANCEL_STUDENT": DisputeType.STUDENT_NO_SHOW,
                "OTP_PREMATURE": DisputeType.WRONG_ABSENT,
                "QUALITY_ISSUE": DisputeType.ATTITUDE_QUALITY,
                "CONTRACT_TERMINATION": DisputeType.CONTRACT_TERMINATION,
            }
            if dt_upper in mapping:
                self.dispute_type = mapping[dt_upper]
            elif hasattr(DisputeType, dt_upper):
                self.dispute_type = DisputeType[dt_upper]
            else:
                self.dispute_type = DisputeType.OTHER
        return self


class CounterDisputeRequest(CamelModel):
    counter_argument: str | None = None
    counter_statement: str | None = None
    counter_evidence_url: str | None = None

    @model_validator(mode="after")
    def _normalize_counter(self) -> "CounterDisputeRequest":
        if not self.counter_argument and self.counter_statement:
            self.counter_argument = self.counter_statement
        if not self.counter_statement and self.counter_argument:
            self.counter_statement = self.counter_argument
        if not self.counter_argument or len(self.counter_argument.strip()) < 5:
            raise ValueError("Nội dung phản biện đối chứng phải có ít nhất 5 ký tự")
        self.counter_argument = self.counter_argument.strip()
        self.counter_statement = self.counter_argument
        return self


class RequestEvidenceRequest(CamelModel):
    admin_notes: str | None = None
    note: str | None = None
    target: str | None = "ALL"  # STUDENT, PT, ALL

    @model_validator(mode="after")
    def _normalize_note(self) -> "RequestEvidenceRequest":
        if not self.admin_notes and self.note:
            self.admin_notes = self.note
        if not self.note and self.admin_notes:
            self.note = self.admin_notes
        if not self.admin_notes or not self.admin_notes.strip():
            raise ValueError("Vui lòng ghi rõ nội dung bằng chứng cần bổ sung")
        self.admin_notes = self.admin_notes.strip()
        self.note = self.admin_notes
        return self


class SubmitAdditionalEvidenceRequest(CamelModel):
    evidence: str

    @field_validator("evidence")
    @classmethod
    def validate_evidence(cls, v: str) -> str:
        s = v.strip() if v else ""
        if not s:
            raise ValueError("Nội dung bằng chứng bổ sung không được để trống")
        return s


class ResolveDisputeRequest(CamelModel):
    action: str | None = None  # 'REFUND_STUDENT', 'PAID_PT', 'RESOLVED_FORCE_MAJEURE', 'CANCEL_CONTRACT_REFUND_STUDENT', 'CANCEL_CONTRACT_PAID_PT'
    verdict_type: str | None = None
    admin_notes: str | None = None
    verdict_reason: str | None = None
    custom_note: str | None = None
    force_override: bool = False
    bypass_48h_waiting: bool | None = None

    @model_validator(mode="after")
    def _normalize_verdict(self) -> "ResolveDisputeRequest":
        if not self.action and self.verdict_type:
            self.action = self.verdict_type
        if not self.verdict_type and self.action:
            self.verdict_type = self.action

        if not self.admin_notes and self.verdict_reason:
            self.admin_notes = self.verdict_reason
        if not self.admin_notes and self.custom_note:
            self.admin_notes = self.custom_note
        if not self.verdict_reason and self.admin_notes:
            self.verdict_reason = self.admin_notes

        if self.bypass_48h_waiting is not None:
            self.force_override = self.force_override or self.bypass_48h_waiting

        if not self.action:
            raise ValueError("Loại phán quyết trọng tài không được để trống")

        act_upper = self.action.upper().strip()
        if act_upper in ("FORCE_MAJEURE", "RESOLVED_FORCE_MAJEURE"):
            self.action = "RESOLVED_FORCE_MAJEURE"
        elif act_upper in ("DISMISS", "REJECTED", "PAID_PT"):
            self.action = "PAID_PT" if act_upper == "PAID_PT" else "REJECTED"

        if not self.admin_notes or len(self.admin_notes.strip()) < 5:
            raise ValueError("Lý do phán quyết của Quản trị viên bắt buộc và phải có ít nhất 5 ký tự")
        self.admin_notes = self.admin_notes.strip()
        return self


