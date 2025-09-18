from pydantic import BaseModel
from typing import Optional

class TaskAssignmentBase(BaseModel):
    task_id: int
    user_id: int

class TaskAssignmentCreate(TaskAssignmentBase):
    pass

class TaskAssignmentOut(BaseModel):
    task_id: int
    user_id: int
    avatar: Optional[str] = None
    name: str