from fastapi import APIRouter, Depends, HTTPException
from ...deps import get_db_connection
from ...users.auth import get_current_user
from ...notifications.crud import notif_crud
from ...notifications.schemas.notif_schema import NotificationCreate, NotificationCreateOut
import asyncpg

router = APIRouter()

@router.post("/", response_model=NotificationCreateOut)
async def post_notification(
    notif: NotificationCreate,
    token: str = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    return await notif_crud.create_notification(conn, notif)

@router.get("/{notification_id}", response_model=dict)
async def fetch_notification(
    notification_id: int,
    token: str = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    return await notif_crud.get_notifications(conn, notification_id)
