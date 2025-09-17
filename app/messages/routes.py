from fastapi import APIRouter, Depends, HTTPException
from ..deps import get_db_connection
from ..users.auth import get_current_user
from .crud import get_few_messages_from_db, get_last_read_timestamp, update_last_read_timestamp,fetch_attachments
from .schemas import MessageReadStatus,GetFiles 
from ..utils.logger import logger
import asyncpg
from datetime import datetime
from typing import List


router = APIRouter()

@router.get("/workspace/{workspace_id}/messages")
async def get_messages(workspace_id: int, last_id:int=None, conn: asyncpg.Connection = Depends(get_db_connection), token:str = Depends(get_current_user)):
    try:
        response = await get_few_messages_from_db(workspace_id, conn, last_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve messages from DB -> {e}")

@router.put("/workspace/{workspace_id}/read-status/{user_id}")
async def update_read_status(workspace_id:int, user_id:int, conn: asyncpg.Connection = Depends(get_db_connection), token:str = Depends(get_current_user)):
    try:
        return await update_last_read_timestamp(workspace_id, user_id, conn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update read_status -> {e}")

@router.get("/workspace/{workspace_id}/read-status/{user_id}")
async def get_last_read_at(workspace_id:int, user_id:int, conn: asyncpg.Connection = Depends(get_db_connection), token:str = Depends(get_current_user)):
    try:
        return await get_last_read_timestamp(workspace_id, user_id, conn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch timestamp -> {e}")
    
    
    
@router.get("/workspace/{workspace_id}/attachments/images", response_model = List [GetFiles])
async def get_image_attachment (
    workspace_id: int,
    conn: asyncpg.Connection = Depends (get_db_connection),
    token:str = Depends(get_current_user)):
    try: 
        return await fetch_attachments (workspace_id, 'image', conn)
    except Exception as e:
        raise HTTPException(status_code=500, detail = f"Process Failed ->{e}")
    
    
@router.get("/workspace/{workspace_id}/attachments/files", response_model = List [GetFiles])
async def get_file_attachment(
    workspace_id: int, 
    conn: asyncpg.Connection = Depends(get_db_connection), 
    token:str = Depends(get_current_user)):
    
    try:
        return await fetch_attachments (workspace_id,'file',conn)
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Process Failed  -> {e}")
    

    

