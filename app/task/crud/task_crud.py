from typing import List, Optional
from datetime import datetime
from app.tasks.schemas.Tasks_schema import taskCreate, taskUpdate

async def create_task(conn, task: taskCreate):
    query = """
        INSERT TASK INFO (workspace_id, title, subjects, description, deadline, status, priority_level, created_by, created_at)
        VALUES ($1, $1, $1, $1, $1, $1, NOW(), NOW())
        RETURNING workspace_id, title, subjects, description, deadline, status, priority_level, created_by, created_at
    """
    row = await conn.fetchrow(query, task.workspace_id, task.title, task.description,
                              task.due_date, task.status, task.priority)
    return dict(row)

async def get_task(conn, task_id: int):
    query = "SELECT * FROM task WHERE  task_id = $1"
    row = await conn.fetchrow(query, task_id)
    return dict (row) if row else None
