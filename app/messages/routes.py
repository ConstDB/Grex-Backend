from fastapi import APIRouter, Depends, HTTPException
from ..deps import get_db_connection
from .crud import get_few_messages_from_db, get_last_read_timestamp, update_last_read_timestamp
from .schemas import MessageReadStatus
from ..utils.logger import logger
import asyncpg
from datetime import datetime



router = APIRouter()

@router.get("/testing")
async def Testing():
    return "hello this is messaging route"


@router.get("/workspace/{workspace_id}/messages")
async def get_messages(workspace_id: int, timestamp:datetime, conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        response = await get_few_messages_from_db(workspace_id, timestamp, conn)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve messages from DB -> {e}")

@router.put("/workspace/{workspace_id}/read-status/{user_id}")
async def update_read_status(workspace_id:int, user_id:int, conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        return await update_last_read_timestamp(workspace_id, user_id, conn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update read_status -> {e}")

@router.get("/workspace/{workspace_id}/read-status/{user_id}")
async def get_last_read_at(workspace_id:int, user_id:int, conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        return await get_last_read_timestamp(workspace_id, user_id, conn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch timestamp -> {e}")