from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal
from decimal import Decimal


class TextMessage(BaseModel):
    text: str

class AttachmentMessage(BaseModel):
    file_url: str
    file_name: str
    file_size: float
    file_type: Literal["file", "image"]

class MessageResponse(BaseModel):
    message_id: int
    workspace_id: int
    sender_id: int
    is_pinned: bool
    avatar: Optional[str]= None
    nickname: str
    type: Literal["text", "attachment", "poll"]
    reply_to: Optional[int] = None
    sent_at: datetime
    content: TextMessage | AttachmentMessage


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
    
class GetFiles(BaseModel):
    attachment_id: int
    message_id:int
    name: str
    type: str 
    url: str
    size:float
    uploaded_at:datetime
    
