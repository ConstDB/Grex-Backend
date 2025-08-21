from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

# shared fields between create/update
class TaskBase(BaseModel):
    title: str
    description: str
    deadline: datetime
    status: Literal["pending", "in_progress", "completed"] = "pending"
    priority_level: Literal["low", "medium", "high"] = "low"
    created_by: int

# creation schema (client does NOT provide created_at or marked_done_at)
class taskCreate(TaskBase):
    pass

# update schema (all fields optional, client can partially update)
class taskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Literal["pending", "in_progress", "completed"] = "pending"
    priority_level: Optional[Literal["low", "medium", "high"]] = None
    marked_done_at: Optional[datetime] = None

# deletion schema (optional message)
class TaskDelete(BaseModel):
    task_id: int
    message: Optional[str] = "Task deleted successfully!"

# output schema (DB fills created_at & marked_done_at)
class TaskOut(TaskBase):
    task_id: int
    created_at: datetime
    marked_done_at: Optional[datetime] = None
