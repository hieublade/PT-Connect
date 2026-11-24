from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, ResourceNotFoundException
from app.models.user import User
from app.repositories.chat_repo import ChatRepository
from app.repositories.user_repo import UserRepository
from app.schemas.requests.chat import SendMessageRequest
from app.schemas.responses.chat import ChatMessageResponse, ConversationResponse


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.user_repo = UserRepository(db)

    def get_messages(self, current_user: User, partner_id: int) -> list[ChatMessageResponse]:
        partner = self.user_repo.get_by_id(partner_id)
        if not partner:
            raise ResourceNotFoundException(f"Không tìm thấy người dùng với ID: {partner_id}")

        # Mark messages sent from partner to current_user as read
        self.chat_repo.mark_as_read(reader_id=current_user.id, partner_id=partner_id)
        self.db.commit()

        messages = self.chat_repo.get_messages_between_users(current_user.id, partner_id)
        return [ChatMessageResponse.from_entity(m) for m in messages]

    def send_message(self, current_user: User, req: SendMessageRequest) -> ChatMessageResponse:
        if req.receiver_id == current_user.id:
            raise BadRequestException("Không thể gửi tin nhắn cho chính mình")

        receiver = self.user_repo.get_by_id(req.receiver_id)
        if not receiver:
            raise ResourceNotFoundException(f"Không tìm thấy người nhận với ID: {req.receiver_id}")

        clean_content = req.content.strip()
        if not clean_content:
            raise BadRequestException("Nội dung tin nhắn không được để trống")

        msg = self.chat_repo.send_message(
            sender_id=current_user.id,
            receiver_id=req.receiver_id,
            content=clean_content,
        )
        self.db.commit()
        self.db.refresh(msg)
        return ChatMessageResponse.from_entity(msg)

    def get_conversations(self, current_user: User) -> list[ConversationResponse]:
        conversations = self.chat_repo.get_conversations_for_user(current_user.id)
        return [ConversationResponse(**c) for c in conversations]

    def mark_as_read(self, current_user: User, partner_id: int) -> int:
        updated = self.chat_repo.mark_as_read(reader_id=current_user.id, partner_id=partner_id)
        self.db.commit()
        return updated
