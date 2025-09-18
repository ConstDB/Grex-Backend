import asyncpg
from fastapi import HTTPException, Depends
from ..deps import get_db_connection

async def fetch_workspace_link_db(workspace_id: int, conn: asyncpg.Connection):
    
    try:
        query = """
        SELECT * FROM quick_links 
        WHERE workspace_id = $1
        ORDER BY created_at DESC;
        
        """
        res = await conn.fetch(query, workspace_id)
        return [dict(row) for row in res]
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"process failed{e}")
        

