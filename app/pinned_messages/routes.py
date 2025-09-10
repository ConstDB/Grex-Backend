from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import date
from ..deps import get_db_connection
import asyncpg
from .crud import workspace_remove_pinned_messages
from .schemas import WorkspacePinnedMessage

router = APIRouter()


@router.get("/workspace/{workspace_id}/pinned-messages/{message_id}")


@router.post("/workspace/{workspace_id}/pinned-messages/{message_id}")




@router.delete("/workspace/{workspace_id}/pinned-messages/{message_id}")

async def workspace_remove_pinned(workspace_id:int, message_id: int,  conn: asyncpg.Connection=Depends(get_db_connection)):
    try: 
        res = await workspace_remove_pinned_messages(workspace_id, message_id,  conn)

        return res 
    except Exception as e: 


        raise HTTPException(status_code=500, detail=f"Process Failed ->{e}")