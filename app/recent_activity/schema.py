from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RecentActivityBase(BaseModel):
    content: str
    created_at: datetime

class RecentActivityCreate(RecentActivityBase):
    pass

class RecentActivityOut(BaseModel):
    activity_id: int
    task_log_id: Optional[int] = None
    workspace_id: int
    content: str
    created_at: datetime