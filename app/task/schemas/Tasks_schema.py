# app/api/task/schemas/Task_schema.py

from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime
class TaskBase(BaseModel):
    title: str
    subject: Optional[str] = None
    description: str
    deadline: datetime
    status: Literal["pending", "in_progress", "completed"] = "pending"
    priority_level: Literal["low", "medium", "high"] = "low"
    created_by: int

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Literal["pending", "done", "overdue"] = "pending"
    priority_level: Optional[Literal["low", "medium", "high"]] = None
    marked_done_at: Optional[datetime] = None

class TaskDelete(BaseModel):
    task_id: int
    message: Optional[str] = "Task deleted successfully!"

class TaskOut(TaskBase):
    task_id: int
    created_at: datetime
    marked_done_at: Optional[datetime] = None
