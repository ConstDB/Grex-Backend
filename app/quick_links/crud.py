import asyncpg
from fastapi import HTTPException, Depends
from ..deps import get_db_connection
from .schemas import CreateLinks,PutLink

async def update_link_db(workspace_id: int, link_id: int, link: PutLink, conn: asyncpg.Connection):
    try:
        query = """
        UPDATE quick_links
        SET link_name = COALESCE($1, link_name),
            link_url  = COALESCE($2, link_url)
        WHERE workspace_id = $3 AND link_id = $4
        RETURNING link_id, workspace_id, link_name, link_url, created_at;
        """
        
        res = await conn.fetchrow(query, link.link_name, link.link_url, workspace_id, link_id)
        
        if not res:
            return None
        return dict(res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to update link -> {e}")

        
         

async def create_workspace_links_db(workspace_id: int, link: CreateLinks, conn: asyncpg.Connection):
    try:
        query = """
        INSERT INTO quick_links(workspace_id, link_name, link_url)
        VALUES ($1, $2, $3)
        RETURNING link_id, workspace_id, message_id, link_name, link_url , created_at
        """
        res = await conn.fetchrow(query, workspace_id, link.link_name, link.link_url)

        if not res:
            return None   
        return dict(res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to add link -> {e}")

    
async def fetch_workspace_link_db(workspace_id: int, conn: asyncpg.Connection):
    try:
        query = """
        
        SELECT * FROM quick_links 
        WHERE workspace_id = $1 
        ORDER BY created_at DESC;
       """
        
        
    # get specific link    
    #   SELECT * FROM quick_links 
    #   WHERE workspace_id = $1 AND link_id = $2
    #   ORDER BY created_at DESC;
        
        
        res = await conn.fetch(query, workspace_id)
        return [dict(row) for row in res]
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"failed to get link{e}")
        
async def remove_workspace_link_db(link_id: int, conn: asyncpg.Connection):
    try:
        query = """
        DELETE FROM quick_links
        where link_id = $1  
        RETURNING *; 
        """
        res = await conn.fetchrow(query, link_id)
        
        return res 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"process failed ->{e}")