from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SubTasksBase(BaseModel):
    subtask_id: int
    task_id: int
    description: str
    is_done: datetime
    created_at: datetime

class SubTasksCreate(SubTasksBase):
    pass

class SubTasksUpdate(BaseModel):
    description: Optional[str] = None
    is_done: datetime
    created_at: datetime

class SubTasksDelete(BaseModel):
    subtask_id: int
    description: str

class SubTasksOut(SubTasksBase):
    subtask_id: int
    is_done: datetime
