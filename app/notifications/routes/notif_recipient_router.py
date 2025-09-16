from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
from ...deps import get_db_connection
from ...users.auth import get_current_user
from ...notifications.crud import notif_recipient_crud
from ..schemas.notif_recipient_schema import NotificationRecipientCreate, NotificationRecipientOut
from ..events import register_listener, push_notifications
from typing import List
import asyncpg

router = APIRouter()

@router.post("/{notification_id}")
async def add_recipients(
    notification_id: int, 
    recipients: List[NotificationRecipientCreate],
    token: str = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    result = await notif_recipient_crud.add_recipients(conn, notification_id, recipients)

    # Notify all recipients via long polling
    for r in recipients:
        await push_notifications(r.user_id, {
            "notification_id": notification_id,
            "content": "You have a new notification",
            "delivered_at": datetime
        })

    return result


@router.get("/", response_model=List[NotificationRecipientOut])
async def fetch_user_notifications(
    user_id: int,
    token: str = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    return await notif_recipient_crud.get_recipients(conn, user_id)

@router.patch("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    user_id: int,
    token: str = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    return await notif_recipient_crud.mark_as_read(conn, user_id, notification_id)


@router.get("/stream")
async def notifications_stream(
    user_id: int,
    token: str = Depends(get_current_user)
):
    """
    Wait until there's a new notification for the user or timeout (30s).
    """
    result = await register_listener(user_id)
    return JSONResponse(result)