from fastapi import HTTPException
from ...utils.decorators import db_error_handler
from ...notifications.schemas.notif_schema import NotificationCreate, NotificationCreateOut

@db_error_handler
async def create_notification(conn, notif: NotificationCreate):
    notif_id = await conn.fetchval(
        """
        INSERT INTO notifications (content)
        values ($1)
        RETURNING notification_id
        """,
    notif.content
    )

    row = await conn.fetchrow(
        "SELECT * FROM notifications WHERE notification_id = $1",
        notif_id
    )
    return NotificationCreateOut(**dict(row))

@db_error_handler
async def get_notifications(conn, notification_id: int):
    row = await conn.fetchrow(
        "SELECT * FROM notifications WHERE notification_id = $1",
        notification_id
    )
    return dict(row) if row else None