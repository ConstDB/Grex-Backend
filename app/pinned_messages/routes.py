from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import date
from ..deps import get_db_connection
import asyncpg
from .crud import get_pinned_messages, pin_workspace_message, workspace_unpin_messages
from .schemas import WorkspacePinnedMessage

router = APIRouter()


@router.get("/workspace/{workspace_id}/pinned-messages/{message_id}")
async def fetch_pinned_message(workspace_id: int, message_id: int, conn: asyncpg.Connection=Depends (get_db_connection)):
    try:
        res = await get_pinned_messages(workspace_id, message_id, conn )
        return res 
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")


@router.post("/workspace/{workspace_id}/pinned-messages/{message_id}")

async def create_pinned_message(workspace_id: int, message_id: int, pinned_by:int, conn: asyncpg.Connection=Depends(get_db_connection)):
    try:
        
        check_query = "SELECT 1 FROM messages WHERE message_id=$1"
        exists = await conn.fetchrow(check_query, message_id)
        if not exists:
            raise HTTPException(status_code=404, detail="Message not found. Cannot pin.")
        
        
        res = await pin_workspace_message (workspace_id, message_id, pinned_by, conn)
        
        return res
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")
    


@router.delete("/workspace/{workspace_id}/pinned-messages/{message_id}")

async def workspace_remove_pinned(workspace_id:int, message_id: int,  conn: asyncpg.Connection=Depends(get_db_connection)):
    try: 
        res = await workspace_unpin_messages(workspace_id, message_id,  conn)

        return res 
    except Exception as e: 


        raise HTTPException(status_code=500, detail=f"Process Failed ->{e}")