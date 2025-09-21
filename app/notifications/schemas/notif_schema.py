from pydantic import BaseModel
from datetime import datetime

class NotificationBase(BaseModel):
    content: str
    created_at: datetime

class NotificationCreate(NotificationBase):
    pass

class NotificationCreateOut(BaseModel):
    content: str
    created_at: datetime

class NotificationOut(BaseModel):
    notification_id: int
    content: str
    workspace_id: int
    created_at: datetime