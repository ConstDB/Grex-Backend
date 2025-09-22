from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Base model (shared fields)
class NotificationRecipientBase(BaseModel):
    notification_id: int
    user_id: int
    is_read: bool = False

# For creating a new recipient entry
class NotificationRecipientCreate(NotificationRecipientBase):
    pass

# For updating (e.g., marking as read)
class NotificationRecipientUpdate(BaseModel):
    is_read: Optional[bool] = None

# For reading (what gets returned in API responses)
class NotificationRecipientOut(NotificationRecipientBase):
    recipient_id: int
    content: str
    workspace_name: Optional[str] = None
    delivered_at: datetime
    is_read: bool = False