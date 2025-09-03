from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import date
from ..deps import get_db_connection
import asyncpg
from ..pinned_messages.schemas import WorkspacePinnedMessage
from .crud import update_pinned_message, workspace_remove_pinned_messages, workspace_pinned_messages
router = APIRouter()


    
@router.post("/workspace/{workspace_id}/pinned-messages/{message_id}")
async def workspace_update_pinned_message(workspace_id: int , message_id: int , pinned_by:int, conn : asyncpg.Connection=Depends(get_db_connection)):
    try: 
        res = await update_pinned_message(workspace_id, message_id, pinned_by, conn )

        return res
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"process failed ->{e}")
    
      
    
@router.get("/workspace/{workspace_id}")
async def workspace_get_pinned_messages(workspace_id:int, message_id:int, pinned_id:int, conn:asyncpg.Connection = Depends(get_db_connection)):
    try:
        res = await workspace_pinned_messages(workspace_id, message_id, pinned_id, conn)
        
        return res 
    except Exception as e: 
        raise HTTPException(status_code=500, detail =f"process failed {e}")
    
    

@router.delete("/workspace/{workspace_id}/pinned-messages/{message_id}")
async def workspace_remove_pinned(workspace_id:int, message_id: int, pinned_by:int, conn: asyncpg.Connection=Depends(get_db_connection)):
    try: 
        res = await workspace_remove_pinned_messages(workspace_id, message_id, pinned_by, conn)
        
        return res 
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Process Failed ->{e}")
    
    