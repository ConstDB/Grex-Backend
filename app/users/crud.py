from fastapi import HTTPException
from ..utils.query_builder import get_query, update_query
import asyncpg


async def fetch_users_by_name(name: str, conn: asyncpg.Connection):
    try:
        query = """
            SELECT user_id, first_name, last_name, email, profile_picture
            FROM users
            WHERE ((first_name || ' ' || last_name) ILIKE '%' || $1 || '%')
            LIMIT 10;
        """

        res = await conn.fetch(query, name)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search user on DB -> {e}")
    

async def fetch_user_data_db(user_id: int, fetch:str, conn: asyncpg.Connection ):
    try: 
        query = get_query("user_id", fetch=fetch, table="users")
    
        res = await conn.fetchrow(query, user_id) 
        return res 
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")
    
async def fetch_social_links_db(user_id: int, fetch:str, conn: asyncpg.Connection ):
    try: 
        query = get_query("user_id", fetch=fetch, table="social_links")
    
        res = await conn.fetchrow(query, user_id) 
        return res 
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")
    
async def partial_update_user_db(user_id: int, payload:dict, conn: asyncpg.Connection):
    query = update_query("user_id", model=payload, table="users")
    res = await conn.fetchrow(query, *payload.values(), user_id)

    return res

async def partial_update_links_db(user_id: int, payload:dict, conn: asyncpg.Connection):
    query = update_query("user_id", model=payload, table="social_links")
    res = await conn.fetchrow(query, *payload.values(), user_id)

    return res

async def fetch_user_tasks_db(user_id:int, conn:asyncpg.Connection):
    query = """
        SELECT 
            t.title,
            t.description,
            t.deadline,
            t.start_date,
            t.task_id,
            t.workspace_id,
            w.name AS workspace_name,
            c.name AS category,
            t.status,
            t.priority_level

        FROM tasks t
        LEFT JOIN workspaces w ON t.workspace_id = w.workspace_id
        LEFT JOIN categories c ON t.category_id = c.category_id
        LEFT JOIN task_assignments ta ON t.task_id = ta.task_id
        WHERE ta.user_id = $1
        ORDER BY t.task_id
    """

    res = await conn.fetch(query, user_id)
    return res

    
async def fetch_current_user_data_db(email: str, conn: asyncpg.Connection, fetch: str="user_id"):
    query = get_query("email", fetch=fetch, table="users")
    return await conn.fetchrow(query, email)