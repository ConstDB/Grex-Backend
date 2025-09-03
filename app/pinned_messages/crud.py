import asyncpg
from fastapi import HTTPException, Depends
from ..deps import get_db_connection
from ..utils.query_builder import insert_query
from ..db_instance import db
import datetime as date



  
async def workspace_pin_message (workspace_id: int, message_id: int, pinned_by:int, conn:asyncpg.Connection):
    try:
        query = """
        INSERT INTO pinned_messages (workspace_id,  message_id, pinned_by )
        VALUES ($1, $2, $3 )
        RETURNING *; 
        """
        res = await conn.fetchrow(query, workspace_id, message_id, pinned_by)
        
        return res
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"process failed")

    
async def workspace_remove_pinned_messages(workspace_id:int, message_id:int, pinned_by:int,  conn: asyncpg.Connection ):
    try:
        query = """
        DELETE FROM pinned_messages
        where workspace_id = $1 
            AND message_id = $2
            AND pinned_by =$3
        RETURNING *;
        

        """
        res = await conn.fetchrow(query, workspace_id, message_id, pinned_by)
        
        return res 
    except Exception as e: 
        raise HTTPException (status_code=500, detail=f"Process failed -> {e}")
    
    
async def update_pinned_message(workspace_id: int, message_id:int, pinned_by:int, pinned_at:date,  conn: asyncpg.Connection):
    try: 
        query = """
        UPDATE pinned_messages 
        SET pinned_at = $1,
        WHERE workspace_id = $2 
        AND message_id = $3
        AND pinned_by = $4
        RETURNING *; 
        """        
        res = await conn.fetchrow(workspace_id, message_id, pinned_by , pinned_at)
        
        return res 
    except Exception as e:
        raise HTTPException (status_code=500, detail=f"procesds failed -> {e}")
    
async def workspace_pinned_messages(workspace_id:int, message_id: int, pinned_by:int, pinned_at:date, conn: asyncpg.Connection):
    try: 
        query = """
        SELECT pinned_messages 
            w.workspace_id
            w.message_id,
            w.pinned_by,
        FROM 
            workspace w
        LEFT JOIN 
            workspace_id wid ON w.messaged_by = wid.pinned_by;
        
        """
        
        res = await conn.fetchrow (workspace_id, message_id, pinned_by, pinned_at)
        
        return res
    except Exception as e:
        raise HTTPException (status_code=500, detail=f"process failed -> {e}")