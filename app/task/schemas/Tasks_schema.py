# app/api/task/schemas/Task_schema.py

from pydantic import BaseModel
from typing import Optional, Literal, List
from datetime import datetime, date


class TaskBase(BaseModel):
    title: str
    subject: Optional[str] = None
    description: str
    deadline: datetime
    status: Literal["pending", "done", "overdue"] = "pending"
    priority_level: Literal["low", "medium", "high"] = "low"
    created_by: int

class TaskCreate(TaskBase):
    pass

class TaskPatch(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[date] = None
    status: Optional[Literal["pending", "done", "overdue"]] = None
    priority_level: Optional[Literal["low", "medium", "high"]] = None
    marked_done_at: Optional[datetime] = None

class TaskDelete(BaseModel):
    task_id: int
    message: Optional[str] = "Task deleted successfully!"

class TaskAllOut(BaseModel):
    task_id: int
    workspace_id: int
    title: str
    subject: str
    description: str
    deadline: Optional[date]
    status: Literal["pending", "done", "overdue"] = "pending"
    priority_level: Optional[Literal["low", "medium", "high"]] = None
    created_by: int
    created_at: datetime
    marked_done_at: Optional[datetime]

# class SubTaskOut(BaseModel):
#     subtask_id: int
#     task_id: int
#     description: str
#     is_done: bool
#     created_at: datetime

# class TaskCommentOut(BaseModel):
#     comment_id: int
#     task_id: int
#     content: str
#     created_at: datetime
#     sender_id: int | None = None

# class TaskAssignmentOut(BaseModel):
#     user_id: int
#     task_id: int

# class TaskAttachmentOut(BaseModel):
#     attachment_id: int
#     file_url: str
#     uploaded_at: datetime

# class TaskOut(TaskBase):
#     task_id: int
#     created_at: datetime
#     marked_done_at: Optional[datetime] = None

#     # Subqueries
#     subtasks: List[SubTaskOut] = []
#     comments: List[TaskCommentOut] = []
#     assignments: List[TaskAssignmentOut] = []
#     attachments: List[TaskAttachmentOut] = []

