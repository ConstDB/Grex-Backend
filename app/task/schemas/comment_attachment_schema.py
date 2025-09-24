from pydantic import BaseModel
from datetime import date
from typing import Optional, Literal

class CommentAttachmentBase(BaseModel):
    name: str
    file_size: int  
    file_type: str
    file_url: str
    uploaded_by: Optional[int] = None


class CreateCommentAttachment(CommentAttachmentBase):
    pass


class CommentAttachmentOut(BaseModel):
    comment_attachment_id: int
    comment_id: int
    task_id: int
    name: str
    file_size: int
    file_type: Optional[Literal["image", "file"]] = None
    file_url: str
    uploaded_by: Optional[int] = None
    uploaded_at: Optional[date] = None
