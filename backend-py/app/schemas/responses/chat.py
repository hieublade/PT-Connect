from datetime import datetime
from typing import Any
from pydantic import BaseModel


class ChatMessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: datetime | None = None
    sender_name: str | None = None
    receiver_name: str | None = None

    @classmethod
    def from_entity(cls, msg: Any) -> "ChatMessageResponse":
        return cls(
            id=msg.id,
            sender_id=msg.sender_id,
            receiver_id=msg.receiver_id,
            content=msg.content,
            is_read=msg.is_read,
            created_at=getattr(msg, "created_at", None),
            sender_name=msg.sender.full_name if getattr(msg, "sender", None) else None,
            receiver_name=msg.receiver.full_name if getattr(msg, "receiver", None) else None,
        )


class ConversationResponse(BaseModel):
    partner_id: int
    partner_name: str
    partner_role: str
    last_message: str
    last_message_at: datetime | None = None
    unread_count: int = 0
