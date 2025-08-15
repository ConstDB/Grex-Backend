from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class TaskAttachmentBase(BaseModel):
    attachment_id: int
    task_id: int
    uploaded_by: str
    file_url: str 
    file_type: Optional[Literal["image", "pdf", "docs"]] = None
