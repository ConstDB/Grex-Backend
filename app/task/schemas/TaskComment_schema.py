from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ...task.schemas.comment_attachment_schema import CommentAttachmentOut, CreateCommentAttachment

class TaskCommentBase(BaseModel):
    content: Optional[str] = None
    sender_id: int
    attachments: Optional["CreateCommentAttachment"] = None

class TaskCommentCreate(TaskCommentBase):
    pass

class CreateCommentOut(BaseModel):
    content: Optional[str] = None 
    sender_id: int
    task_id: int
    attachments: Optional["CommentAttachmentOut"] = None

class TaskCommentUpdate(BaseModel):
    content: str

class TaskCommentDelete(BaseModel):
    comment_id: int

class TaskCommentOut(BaseModel):
    comment_id: int
    task_id: int
    content: Optional[str] = None
    created_at: datetime 
    sender_id: int
    profile_picture: Optional[str] = None
    sender_name: str
    attachments: Optional[CommentAttachmentOut] = None