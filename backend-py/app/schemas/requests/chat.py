from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    receiver_id: int = Field(..., description="ID của người nhận tin nhắn")
    content: str = Field(..., min_length=1, max_length=5000, description="Nội dung tin nhắn")
