from fastapi import APIRouter, Depends, HTTPException
from ..deps import get_db_connection
from ..authentication.services import get_current_user
from .crud import get_few_messages_from_db, get_last_read_timestamp, update_last_read_timestamp,fetch_attachments_db, fetch_replied_message_db
from .schemas import MessageReadStatus,GetFiles , MessageResponse
from ..utils.logger import logger
import json
import asyncpg
from datetime import datetime
from typing import List


router = APIRouter()

@router.get("/workspace/{workspace_id}/messages")
async def get_messages(workspace_id: int, last_id:int=None, conn: asyncpg.Connection = Depends(get_db_connection), token:str = Depends(get_current_user)):
    try:
        responses = await get_few_messages_from_db(workspace_id, conn, last_id)

        processed_data = []

        for response in responses:
            result = dict(response)
            result["content"] = json.loads(result["content"])

            print(result)
            processed_data.append(MessageResponse(**result))

        return processed_data

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
async def get_image_attachment_route (
    workspace_id: int,
    conn: asyncpg.Connection = Depends (get_db_connection),
    token:str = Depends(get_current_user)):
    try: 
        return await fetch_attachments_db (workspace_id, 'image', conn)
    except Exception as e:
        raise HTTPException(status_code=500, detail = f"Process Failed ->{e}")
    
     
@router.get("/workspace/{workspace_id}/attachments/files", response_model = List [GetFiles])
async def get_file_attachment_route(
    workspace_id: int, 
    conn: asyncpg.Connection = Depends(get_db_connection), 
    token:str = Depends(get_current_user)):
    
    try:
        return await fetch_attachments_db (workspace_id,'file',conn)
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Process Failed  -> {e}")
    
@router.get("/workspaces/{workspace_id}/messages/{message_id}/replies")
async def get_replied_message_route(
    workspace_id:int,
    message_id: int,
    conn: asyncpg.Connection = Depends(get_db_connection),
    token: str = Depends(get_current_user)
):
    return await fetch_replied_message_db(message_id, workspace_id, conn)


    

    

