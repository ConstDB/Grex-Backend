from pydantic import BaseModel
from typing import Optional

class TaskAssignmentBase(BaseModel):
    task_id: int
    user_id: int

class TaskAssignmentCreate(TaskAssignmentBase):
    pass

class TaskAssignmentUpdate(BaseModel):
    task_id: Optional[int] = None
    user_id: Optional[int] = None
