from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskCommentBase(BaseModel):
    content: str
    sender_id: int

class TaskCommentCreate(TaskCommentBase):
    pass

class TaskCommentUpdate(BaseModel):
    content: str

class TaskCommentDelete(BaseModel):
    comment_id: int

class TaskCommentOut(TaskCommentBase):
    comment_id: int
    task_id: int
    created_at: datetime 
    sender_id: int
    profile_picture: Optional[str] = None