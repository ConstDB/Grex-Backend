from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal

class Message_Base(BaseModel):
    message_id: int
    workspace_id: int
    sender_id: int
    message_type: Literal["text", "image", "file", "poll"] = "text"
    reply_to: Optional[int] = None

class Message_Create(Message_Base):
    pass

class Message_read(BaseModel):
    message_id: int
    sent_at: datetime

    class config:
        from_attributes = True 

class MessageUpdate(BaseModel):
    content: Optional[str] = None
    Message_type: Optional[Literal["text", "image", "file", "poll"]] = None


class MessageReadStatus(BaseModel):
    last_read_at: datetime
