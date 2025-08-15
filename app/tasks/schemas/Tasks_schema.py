from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    task_id: int
    workspace_id: int
    subject: str
    title: str
    description: str
    deadline: datetime
    status: str
    priority_level: str
    created_by: str
    created_at: datetime
    marked_done_at: datetime

class taskCreate(TaskBase):
    pass

class taskUpdate(BaseModel):
    subject: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None
    priority_level: str
    marked_done_at: datetime

class TaskDelete(BaseModel):
    task_id: int
    message: str

class TaskOut(TaskBase):
    task_id: int
    created_at: datetime
    marked_done_at: Optional[datetime]

