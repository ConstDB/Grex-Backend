from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskLogBase(BaseModel):
    workspace_id:int
    context: str
    created_at: datetime

class TaskLogCreate(TaskLogBase):
    pass

class TaskLogUpdate(BaseModel):
    context: Optional[str] = None

class TaskLogRead(TaskLogBase):
    pass