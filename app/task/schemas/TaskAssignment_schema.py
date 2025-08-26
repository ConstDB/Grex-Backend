from pydantic import BaseModel
from typing import Optional

class TaskAssignmentBase(BaseModel):
    task_id: int
    user_id: int

class TaskAssignmentCreate(TaskAssignmentBase):
    pass
