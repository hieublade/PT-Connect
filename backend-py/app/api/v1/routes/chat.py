from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.responses import created_response, ok_response
from app.models.user import User
from app.schemas.requests.chat import SendMessageRequest
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/conversations")
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChatService(db)
    res = service.get_conversations(current_user)
    return ok_response(
        data=[c.model_dump(mode="json") for c in res],
        message="Lấy danh sách cuộc hội thoại thành công",
    )


@router.get("/messages/{partner_id}")
def get_messages(
    partner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChatService(db)
    res = service.get_messages(current_user, partner_id)
    return ok_response(
        data=[m.model_dump(mode="json") for m in res],
        message="Lấy lịch sử tin nhắn thành công",
    )


@router.post("/send", status_code=201)
def send_message(
    request: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChatService(db)
    res = service.send_message(current_user, request)
    return created_response(
        data=res.model_dump(mode="json"),
        message="Gửi tin nhắn thành công",
        status_code=201,
    )


@router.post("/read/{partner_id}")
def mark_read(
    partner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChatService(db)
    count = service.mark_as_read(current_user, partner_id)
    return ok_response(
        data={"updated_count": count},
        message=f"Đã đánh dấu {count} tin nhắn là đã đọc",
    )
