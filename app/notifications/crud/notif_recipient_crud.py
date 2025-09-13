from fastapi import HTTPException
from ...utils.decorators import db_error_handler
from ..schemas.notif_recipient_schema import NotificationRecipientCreate

@db_error_handler
async def add_recipients(conn, notification_id: int, recipients: list[NotificationRecipientCreate]):
    for recipient in recipients:
        await conn.execute(
            """
            INSERT INTO notification_recipients (notification_id, user_id, workspace_id)
            VALUES ($1, $2, $3)
            """,
            notification_id, recipient.user_id, recipient.workspace_id,
        )
    return {"status": "recipients added"}


@db_error_handler
async def get_recipients(conn, user_id: int):
    query = "SELECT * FROM notification_recipients WHERE user_id = $1"
    rows = await conn.fetch(query, user_id)
    return [dict(r) for r in rows]


async def mark_as_read(conn, user_id: int, notification_id: int):
    result = await conn.execute(
        """
        UPDATE notification_recipients
        SET is_read = TRUE
        WHERE user_id = $1 AND notification_id = $2
        """,
        user_id, notification_id
    )
    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "marked as read"}
