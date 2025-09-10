
import asyncpg
from fastapi import HTTPException, Depends
from ..deps import get_db_connection
from ..utils.query_builder import insert_query
from ..db_instance import db
from datetime import datetime
from .schemas import WorkspaceGetPinnedMessage, WorkspacePinnedMessage, WorkspaceRemovePinnedMessage


    
async def get_pinned_messages(workspace_id:int,  conn: asyncpg.Connection):
    try:

        query = """
        SELECT * FROM  pinned_messages 
        WHERE workspace_id = $1
        ORDER BY pinned_at DESC;
        """

        res = await conn.fetch (query, workspace_id)
        return res
    except Exception as e:
        raise HTTPException (status_code=500, detail=f"process failed -> {e}")
    
async def pin_workspace_message (workspace_id:int, message_id: int, conn: asyncpg.Connection):
    pass
    """try: 
        pass"""

async def workspace_remove_pinned_messages(workspace_id:int, message_id:int, conn: asyncpg.Connection ):
    try:

        query = """
        DELETE FROM pinned_messages
        where workspace_id = $1 
            AND message_id = $2
        RETURNING *;
        """
        res = await conn.fetchrow(query, workspace_id, message_id )

        return res 
    except Exception as e: 

        raise HTTPException (status_code=500, detail=f"Process failed -> {e}")