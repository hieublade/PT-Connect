import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_roles
from app.core.exceptions import BadRequestException
from app.core.responses import created_response, ok_response
from app.models.enums import DisputeStatus, Role
from app.models.user import User
from app.schemas.requests.dispute import (
    CreateDisputeRequest,
    CounterDisputeRequest,
    RequestEvidenceRequest,
    ResolveDisputeRequest,
)
from app.services.dispute_service import DisputeService

router = APIRouter(prefix="/disputes", tags=["Disputes"])

UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload-evidence")
async def upload_dispute_evidence(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload ảnh bằng chứng / phản biện cho tranh chấp ca tập."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise BadRequestException("Chỉ chấp nhận file định dạng hình ảnh (PNG, JPG, JPEG, WEBP)")

    ext = Path(file.filename or "evidence.jpg").suffix or ".jpg"
    safe_filename = f"evidence_{uuid.uuid4().hex[:12]}{ext}"
    dest_path = UPLOAD_DIR / safe_filename

    content = await file.read()
    with open(dest_path, "wb") as f:
        f.write(content)

    file_url = f"/static/uploads/{safe_filename}"
    return ok_response(
        data={"url": file_url, "filename": safe_filename},
        message="Tải lên ảnh bằng chứng thành công",
    )


@router.post("", status_code=201)
def create_dispute(
    request: CreateDisputeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DisputeService(db)
    res = service.create_dispute(current_user, request)
    return created_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Gửi khiếu nại thành công. Bên bị khiếu nại có 48 giờ để gửi phản biện.",
        status_code=201,
    )


@router.get("")
def list_disputes(
    status: DisputeStatus | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DisputeService(db)
    disputes = service.list_disputes(current_user, status)
    return ok_response(
        data=[d.model_dump(mode="json", by_alias=True) for d in disputes],
        message="Lấy danh sách khiếu nại thành công",
    )


@router.get("/{dispute_id}")
def get_dispute_detail(
    dispute_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DisputeService(db)
    res = service.get_dispute(dispute_id, current_user)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Lấy chi tiết khiếu nại thành công",
    )


@router.post("/{dispute_id}/counter")
def submit_counter_argument(
    dispute_id: int,
    request: CounterDisputeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DisputeService(db)
    res = service.submit_counter_argument(dispute_id, current_user, request)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Gửi thông tin phản biện và bằng chứng thành công",
    )


@router.post("/{dispute_id}/request-evidence")
def request_more_evidence(
    dispute_id: int,
    request: RequestEvidenceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = DisputeService(db)
    res = service.request_more_evidence(dispute_id, current_user, request)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Đã gửi yêu cầu bổ sung bằng chứng (thời hạn 48 giờ)",
    )


@router.post("/{dispute_id}/resolve")
def resolve_dispute(
    dispute_id: int,
    request: ResolveDisputeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = DisputeService(db)
    res = service.resolve_dispute(dispute_id, current_user, request)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Phán quyết khiếu nại thành công và đã gửi kết luận cho hai bên",
    )

