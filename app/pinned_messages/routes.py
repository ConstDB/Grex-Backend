from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import date
from ..deps import get_db_connection
import asyncpg
from .crud import fetch_pinned_messages_db, insert_pinned_message_db, unpin_messages_db, update_message_db
from .schemas import PinnedMessagesPayload
from ..authentication.services import get_current_user


router = APIRouter()


@router.get("/workspace/{workspace_id}/pinned/message", response_model=List[PinnedMessagesPayload])
async def get_pinned_messages_route(workspace_id: int,  conn: asyncpg.Connection=Depends(get_db_connection), token: str=Depends(get_current_user)):
    try:
        messages = await fetch_pinned_messages_db(workspace_id, conn )
        return [PinnedMessagesPayload(**message) for message in messages] 
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")

@router.post("/workspace/{workspace_id}/pinned-messages/{message_id}", response_model=PinnedMessagesPayload)
async def create_pinned_messages_route(workspace_id: int, message_id: int, pinned_by:int, conn: asyncpg.Connection=Depends(get_db_connection), token: str=Depends(get_current_user)):
    try:        
        res = await insert_pinned_message_db (workspace_id, message_id, pinned_by, conn)
        await update_message_db(message_id, conn)
        return res
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")

@router.delete("/workspace/{workspace_id}/pinned-messages/{message_id}", response_model=PinnedMessagesPayload)
async def remove_pinned_messages_route(workspace_id:int, message_id: int,  conn: asyncpg.Connection=Depends(get_db_connection), token: str=Depends(get_current_user)):
    try: 
        res = await unpin_messages_db(workspace_id, message_id,  conn)
        await update_message_db(message_id, conn, is_pin=False)
        return res 
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Process Failed ->{e}")