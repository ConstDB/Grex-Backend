import asyncpg
from fastapi import HTTPException


async def add_workspace_to_db(workspace:dict, conn: asyncpg.Connection):
    try:
        query = """
            INSERT INTO workspaces (name, description, project_nature, start_date, due_date) VALUES ($1, $2, $3, $4, $5) RETURNING *
        """
        
        res = await conn.fetchrow(query, *workspace.values())
        
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong -> {e}")