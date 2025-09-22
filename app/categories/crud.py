from ..categories.schema import CategoryCreate, CategoryUpdate, CategoryDelete
from datetime import datetime
from ..utils.query_builder import get_query
from ..utils.decorators import db_error_handler
from ..users.crud import fetch_current_user_data_db
from fastapi import HTTPException
import asyncpg

# For Creating Category
async def insert_category_db(conn, workspace_id: int, email:str,  category: CategoryCreate):
    
    user = await fetch_current_user_data_db(email, conn)

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required to create tasks")

    creator_role = await fetch_role_db(conn, workspace_id, user["user_id"])

    if creator_role == "member":
        raise HTTPException(status_code=403, detail="You do not have permission to create tasks")

    query = """
        INSERT INTO categories (workspace_id, name)
        VALUES ($1, $2)
        RETURNING category_id, workspace_id, name, created_at
    """
    row = await conn.fetchrow(query, workspace_id, category.name)
    return dict(row) if row else None

# Get Category
@db_error_handler
async def fetch_category_db(conn, workspace_id: int):
    query = """
        SELECT *
        FROM categories 
        WHERE workspace_id = $1 
    """
    rows = await conn.fetch(query, workspace_id)
    return [dict(r) for r in rows]


async def fetch_role_db(conn: asyncpg.Connection, workspace_id: int, user_id: int):
    query= get_query("workspace_id", "user_id", fetch="role", table="workspace_members")
    return await conn.fetchval(query, workspace_id, user_id)

# Update category
@db_error_handler
async def update_category_db(conn, workspace_id: int, category_id: int, update_category:CategoryUpdate):
    query = f"UPDATE categories SET name = COALESCE($3, name) WHERE workspace_id = $1 AND category_id = $2 RETURNING *;"
    rows = await conn.fetchrow(query, 
                               workspace_id, 
                               category_id, 
                               update_category.name)
    return dict(rows)

# Delete category
@db_error_handler
async def delete_category_db(conn, workspace_id: int, category_id: int):
    query = """
        DELETE FROM categories 
        WHERE workspace_id = $1 AND category_id = $2 
        RETURNING *
    """
    row = await conn.fetchrow(query, workspace_id, category_id)
    return dict(row) if row else None
