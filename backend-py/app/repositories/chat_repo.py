from sqlalchemy import or_, and_, desc
from sqlalchemy.orm import Session, joinedload

from app.models.chat_message import ChatMessage
from app.models.user import User


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_messages_between_users(self, user_a: int, user_b: int) -> list[ChatMessage]:
        return (
            self.db.query(ChatMessage)
            .options(joinedload(ChatMessage.sender), joinedload(ChatMessage.receiver))
            .filter(
                or_(
                    and_(ChatMessage.sender_id == user_a, ChatMessage.receiver_id == user_b),
                    and_(ChatMessage.sender_id == user_b, ChatMessage.receiver_id == user_a),
                )
            )
            .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
            .all()
        )

    def send_message(self, sender_id: int, receiver_id: int, content: str) -> ChatMessage:
        msg = ChatMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content.strip(),
            is_read=False,
        )
        self.db.add(msg)
        self.db.flush()
        return msg

    def mark_as_read(self, reader_id: int, partner_id: int) -> int:
        updated = (
            self.db.query(ChatMessage)
            .filter(
                ChatMessage.sender_id == partner_id,
                ChatMessage.receiver_id == reader_id,
                ChatMessage.is_read == False,  # noqa: E712
            )
            .update({"is_read": True}, synchronize_session=False)
        )
        self.db.flush()
        return updated

    def get_conversations_for_user(self, user_id: int) -> list[dict]:
        # Query distinct partner IDs that have chat messages with this user
        all_msgs = (
            self.db.query(ChatMessage)
            .options(joinedload(ChatMessage.sender), joinedload(ChatMessage.receiver))
            .filter(or_(ChatMessage.sender_id == user_id, ChatMessage.receiver_id == user_id))
            .order_by(desc(ChatMessage.created_at), desc(ChatMessage.id))
            .all()
        )

        conversations_map: dict[int, dict] = {}
        for m in all_msgs:
            partner = m.receiver if m.sender_id == user_id else m.sender
            partner_id = partner.id if partner else (m.receiver_id if m.sender_id == user_id else m.sender_id)

            if partner_id not in conversations_map:
                role_val = getattr(partner.role, "value", str(partner.role)) if partner and hasattr(partner, "role") else "USER"
                conversations_map[partner_id] = {
                    "partner_id": partner_id,
                    "partner_name": partner.full_name if partner else f"User #{partner_id}",
                    "partner_role": role_val,
                    "last_message": m.content,
                    "last_message_at": m.created_at,
                    "unread_count": 0,
                }

            if m.receiver_id == user_id and not m.is_read:
                conversations_map[partner_id]["unread_count"] += 1

        return list(conversations_map.values())
