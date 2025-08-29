# app/api/task/crud/task_crud.py
from app.utils.decorators import db_error_handler
from datetime import date, datetime
from app.utils.task_logs import log_task_action

# Assigning users to a specific task
@db_error_handler
async def create_taskassignment(conn, task_id, user_id):
    query = """
            INSERT INTO task_assignments(task_id, user_id)
            VALUES ($1, $2)
            RETURNING task_id, user_id
        """
    row = await conn.fetchrow(query, task_id, user_id)
    return dict(row)

# Get assigned users from a task
@db_error_handler
async def get_taskassignment(conn, task_id: int):
    query = """
            SELECT 
                ta.task_id,
                ta.user_id,
                u.profile_picture AS avatar,
                (u.first_name || ' ' || u.last_name) AS name        
            FROM task_assignments ta
            LEFT JOIN users u ON u.user_id = ta.user_id
            WHERE ta.task_id = $1 
            ORDER BY ta.task_id ASC;
        """
    rows = await conn.fetch(query, task_id)
    return [dict(row) for row in rows] if rows else None

# Unassign users from task
@db_error_handler
async def delete_taskassignment(conn, task_id:int, user_id:int):

    query = "DELETE FROM task_assignments WHERE task_id=$1 AND user_id=$2 RETURNING *;"
    row = await conn.fetchrow(query, task_id, user_id)
    return dict(row) if row else None
