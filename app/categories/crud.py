from ..categories.schema import CategoryCreate, CategoryUpdate, CategoryOut
from datetime import datetime
from ..utils.decorators import db_error_handler
from ..utils.task_logs import log_task_action

# For Creating Category
@db_error_handler
async def create_category(conn, workspace_id: int, create_category: CategoryCreate):
    query = """
        INSERT INTO categories(category_id, workspace_id, name, created_at)
        VALUES ($1, $2, $3, $4)
        RETURNING *;
    """
    row = await conn.fetchrow(query, 
                              workspace_id, 
                              create_category.category_id, 
                              create_category.name,
                              create_category.created_at)
    return dict(row) 

# Get Category
@db_error_handler
async def get_category(conn, workspace_id: int, category_id: int, get_category:CategoryOut):
    query = """
        SELECT *
        FROM categories 
        WHERE workspace_id = $1 AND category_id = $2
    """
    rows = await conn.fetchrow(query, workspace_id, category_id)
    return [dict(r) for r in rows]

async def update_category(conn, workspace_id: int, category_id: int, update_category:CategoryUpdate):
    query = f"UPDATE subtasks SET name = COALESCE($3, name) WHERE workspace_id = $1 AND category_id = $2 RETURNING *;"
    rows = await conn.fetchrow(conn, 
                               workspace_id, 
                               category_id, 
                               update_category.name)
    return dict(rows)

async def delete_category(conn, workspace_id: int, category_id: int):
    query = "DELETE FROM categories WHERE workspace_id = $1 AND category_id = $2 RETURNING *;"
    rows = await conn.fetchrow(conn, workspace_id, category_id)
    return dict(rows)