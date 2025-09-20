from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional

class GetPinnedMessage(BaseModel):
    workspace_id: int 
    message_id:int
    pinned_by: int 
    pinned_at:datetime


class PinnedMessagesResponse(BaseModel):
    message_id: int
    workspace_id: int
    sender_id: int
    is_pinned: Optional[bool] = None
    profile_picture: Optional[str] = None
    nickname: Optional[str] = None
    message_type: str
    reply_to: Optional[int] = None
    sent_at: datetime
    content: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    question: Optional[str] = None
    pinned_by: Optional[str] = None
    pinned_at: datetime

class PinnedMessagesPayload(BaseModel):
    message_id:int
    pinned_by:int
    pinned_at:datetime
    workspace_id: int
    
class RemovePinnedMessage(BaseModel):
    workspace_id: int 
    message_id: int 

    
