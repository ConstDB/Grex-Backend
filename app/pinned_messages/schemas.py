from pydantic import BaseModel
from typing import Optional, List
from ..users.schemas import UserBasic, UserDetail
from datetime import date, datetime
from ..messages.schemas import Message_Base


class WorkspaceGetPinnedMessage():
    pass 

class WorkspacePinnedMessage(BaseModel):
    workspace_id: int
    message_id: int
    sender_id: int 
    pinned_message: str
    pinned_by: int  
    pinned_at: date 
    
class WorkspaceRemovePinnedMessage():
    pass 
    
