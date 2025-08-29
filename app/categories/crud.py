from ..categories.schema import CategoryCreate, CategoryUpdate, CategoryDelete
from datetime import datetime
from ..utils.decorators import db_error_handler
from ..utils.task_logs import log_task_action

# For Creating Category
@db_error_handler
async def create_category(conn, workspace_id: int, category: CategoryCreate):
    query = """
        INSERT INTO categories (workspace_id, name)
        VALUES ($1, $2)
        RETURNING category_id, workspace_id, name, created_at
    """
    row = await conn.fetchrow(query, workspace_id, category.name)
    return dict(row) if row else None

# Get Category
@db_error_handler
async def get_category(conn, workspace_id: int):
    query = """
        SELECT *
        FROM categories 
        WHERE workspace_id = $1 
    """
    rows = await conn.fetch(query, workspace_id)
    return [dict(r) for r in rows]


async def update_category(conn, workspace_id: int, category_id: int, update_category:CategoryUpdate):
    query = f"UPDATE categories SET name = COALESCE($3, name) WHERE workspace_id = $1 AND category_id = $2 RETURNING *;"
    rows = await conn.fetchrow(query, 
                               workspace_id, 
                               category_id, 
                               update_category.name)
    return dict(rows)

async def delete_category(conn, workspace_id: int, category_id: int):
    query = """
        DELETE FROM categories 
        WHERE workspace_id = $1 AND category_id = $2 
        RETURNING *
    """
    row = await conn.fetchrow(query, workspace_id, category_id)
    return dict(row) if row else None
