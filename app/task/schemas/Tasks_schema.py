# app/api/task/schemas/Task_schema.py

from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime, date


class TaskBase(BaseModel):
    category: str
    title: str
    subject: Optional[str] = None
    description: str
    deadline: Optional[datetime] = None
    status: Literal["pending", "done", "overdue"] = "pending"
    priority_level: Literal["low", "medium", "high"] = "low"
    start_date: Optional[date] = None
    created_by: int

class TaskCreate(TaskBase):
    pass

class TaskCreateOut(BaseModel):
    category: str 
    title: str
    subject: str
    description: str
    deadline: Optional[datetime]
    status: Literal["pending", "done", "overdue"] = "pending"
    priority_level: Optional[Literal["low", "medium", "high"]] = None
    start_date: Optional[date] = None
    created_by: int
    created_at: datetime

class TaskPatch(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[Literal["pending", "done", "overdue"]] = None
    priority_level: Optional[Literal["low", "medium", "high"]] = None
    start_date: Optional[date] = None
    marked_done_at: Optional[datetime] = None

class TaskDelete(BaseModel):
    task_id: int
    message: Optional[str] = "Task deleted successfully!"

class TaskAllOut(BaseModel):
    task_id: int
    workspace_id: int
    category: str
    title: str
    subject: str
    description: str
    deadline: Optional[datetime]
    status: Literal["pending", "done", "overdue"] = "pending"
    priority_level: Optional[Literal["low", "medium", "high"]] = None
    start_date: Optional[date] = None
    created_by: int
    created_at: datetime
    marked_done_at: Optional[datetime]

