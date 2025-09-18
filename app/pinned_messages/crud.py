
import asyncpg
from fastapi import HTTPException, Depends
from ..deps import get_db_connection
from ..utils.query_builder import insert_query, update_query
from ..db_instance import db
from datetime import datetime
from .schemas import PinnedMessagesPayload
    
async def fetch_pinned_messages_db(workspace_id:int,  conn: asyncpg.Connection):
    try:
        query = """
        SELECT 
            md.*,
            wm.nickname AS pinned_by,
            pm.pinned_at
        FROM pinned_messages pm
        JOIN message_details md ON pm.message_id = md.message_id
        LEFT JOIN workspace_members wm ON wm.user_id = pm.pinned_by AND wm.workspace_id = $1
        AND pm.workspace_id = md.workspace_id
        WHERE pm.workspace_id = $1
        ORDER BY pm.pinned_at DESC;
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
    

async def update_message_db(message_id:int, conn: asyncpg.Connection , is_pin: bool=True):
    payload = {
        "is_pinned": is_pin
    }
    query = update_query("message_id", model=payload, table="messages")

    await conn.execute(query, *payload.values(), message_id)
