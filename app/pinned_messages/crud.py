
import asyncpg
from fastapi import HTTPException, Depends
from ..deps import get_db_connection
from ..utils.query_builder import insert_query
from ..db_instance import db
from datetime import datetime
from .schemas import PinnedMessagesPayload
    
async def fetch_pinned_messages_db(workspace_id:int,  conn: asyncpg.Connection):
    try:
        query = """
        SELECT * FROM pinned_messages 
        WHERE workspace_id = $1
        ORDER BY pinned_at DESC;
        """
        res = await conn.fetch(query, workspace_id)
        
        return res
    except Exception as e:
        raise HTTPException (status_code=500, detail=f"process failed -> {e}")
    
async def insert_pinned_message_db (workspace_id:int, message_id: int, pinned_by:int, conn: asyncpg.Connection):
    try:
        query = """
        INSERT INTO pinned_messages
        (workspace_id, message_id, pinned_by)
        VALUES ($1, $2, $3)
        RETURNING *;  
        """
        res = await conn.fetchrow(query, workspace_id, message_id, pinned_by)
        if res:
            return dict(res)
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")
                

async def unpin_messages_db(workspace_id:int, message_id:int, conn: asyncpg.Connection ):
    try:
        query = """
        DELETE FROM pinned_messages
        where workspace_id = $1 
            AND message_id = $2
        RETURNING *;
        """
        res = await conn.fetchrow(query, workspace_id, message_id )

        if res:
            return dict(res) 
    except Exception as e: 

        raise HTTPException (status_code=500, detail=f"Process failed -> {e}")