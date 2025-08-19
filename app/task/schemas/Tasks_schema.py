from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    subject: str
    title: str
    description: str
    deadline: datetime
    status: str
    priority_level: str
    created_by: int
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
    priority_level: Optional[str] = None
    marked_done_at: Optional[datetime] = None

class TaskDelete(BaseModel):
    task_id: int
    message: Optional[str] = "Task deleted successfully!"   

class TaskOut(TaskBase):
    task_id: int
    created_at: datetime
    marked_done_at: Optional[datetime] = None

