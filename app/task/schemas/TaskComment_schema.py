from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class taskCommentBase(BaseModel):
    content: str
    created_at: datetime
    sender_id: int

class taskCommentCreate(taskCommentBase):
    pass

class taskCommentUpdate(BaseModel):
    content: Optional[str] = None

class taskCommentDelete(taskCommentBase):
    pass

