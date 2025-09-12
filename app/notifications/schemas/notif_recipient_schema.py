from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Base model (shared fields)
class NotificationRecipientBase(BaseModel):
    notification_id: int
    user_id: int
    workspace_id: Optional[int] = None  # can be NULL for personal/global notifs
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
    delivered_at: datetime