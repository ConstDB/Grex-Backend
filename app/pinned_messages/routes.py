from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import date
from ..deps import get_db_connection
import asyncpg
from .crud import update_pinned_message, workspace_remove_pinned_messages, workspace_pinned_messages
from .schemas import WorkspacePinnedMessage

router = APIRouter()
@router.post("/workspace/{workspace_id}/pinned-messages/{message_id}")

async def workspace_update_pinned_message(workspace_id: int, payload:WorkspacePinnedMessage, conn : asyncpg.Connection=Depends(get_db_connection)):
    try: 
        res = await update_pinned_message(workspace_id, payload, conn )
        return res
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"process failed ->{e}")

@router.get("/workspace/{workspace_id}/pinned-messages")


async def workspace_get_pinned_messages(workspace_id:int, conn:asyncpg.Connection = Depends(get_db_connection)):
    try:
        res = await workspace_pinned_messages(workspace_id, conn)
        return res 
    except Exception as e: 
        raise HTTPException(status_code=500, detail =f"process failed {e}")


@router.delete("/workspace/{workspace_id}/pinned-messages/{message_id}")

async def workspace_remove_pinned(workspace_id:int, message_id: int,  conn: asyncpg.Connection=Depends(get_db_connection)):
    try: 
        res = await workspace_remove_pinned_messages(workspace_id, message_id,  conn)

        return res 
    except Exception as e: 


        raise HTTPException(status_code=500, detail=f"Process Failed ->{e}")