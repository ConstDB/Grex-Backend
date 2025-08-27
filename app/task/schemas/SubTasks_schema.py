from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SubTasksBase(BaseModel):
    description: str
    is_done: bool = False

class SubTasksCreate(SubTasksBase):
    pass

class SubTasksPatch(BaseModel):
    description: Optional[str] = None
    is_done: Optional[bool] = None  

class SubTasksOut(BaseModel):
    subtask_id: int
    task_id: int
    description: str
    is_done: bool
    created_at: datetime
