from datetime import datetime, timezone
from typing import List, Optional

async def create_notification(conn, content: str, workspace_id: Optional[int] = None):
    """Insert a new notification event and return its ID."""
    row = await conn.fetchrow("""
        INSERT INTO notifications (content, workspace_id, created_at)
        VALUES ($1, $2, $3)
        RETURNING notification_id
    """, content, workspace_id, datetime.now(timezone.utc))
    return row["notification_id"]

async def add_recipients(conn, notification_id: int, user_ids: List[int], workspace_id: Optional[int] = None):
    """Attach notification to multiple users."""
    for uid in user_ids:
        await conn.execute("""
            INSERT INTO notification_recipients (notification_id, user_id, workspace_id, is_read, delivered_at)
            VALUES ($1, $2, $3, FALSE, $4)
        """, notification_id, uid, workspace_id, datetime.now(timezone.utc))
