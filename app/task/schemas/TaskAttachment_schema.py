from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class TaskAttachmentBase(BaseModel):
    task_id: int
    file_url: str 
    file_type: Optional[Literal["image", "pdf", "docs"]] = None
    file_size: Optional[float] = None
    uploaded_by: int
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class TaskAttachmentCreate(TaskAttachmentBase):
    pass

class TaskAttachmentDelete(BaseModel):
    attachment_id: int
    task_id: int

class TaskAttachmentRead(TaskAttachmentBase):
    attachment_id: int