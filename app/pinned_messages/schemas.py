from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional
from ..messages.schemas import MessageResponse

class GetPinnedMessage(BaseModel):
    workspace_id: int 
    message_id:int
    pinned_by: int 
    pinned_at:datetime


class PinnedMessagesResponse(MessageResponse):
    pinned_by: str
    pinned_at: datetime

class PinnedMessagesPayload(BaseModel):
    message_id:int
    pinned_by:int
    pinned_at:datetime
    workspace_id: int
    
class RemovePinnedMessage(BaseModel):
    workspace_id: int 
    message_id: int 

    
