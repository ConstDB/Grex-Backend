from fastapi import APIRouter, Depends, HTTPException
from ...deps import get_db_connection
from ...users.auth import get_current_user
from ...notifications.crud import notif_recipient_crud
from ..schemas.notif_recipient_schema import NotificationRecipientCreate, NotificationRecipientOut
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
    return await notif_recipient_crud.add_recipients(conn, notification_id, recipients)

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
