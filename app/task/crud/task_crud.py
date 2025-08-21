from datetime import datetime
from app.task.schemas.Tasks_schema import taskCreate, taskUpdate, TaskDelete
from datetime import datetime, timezone

now = datetime.now(timezone.utc)  # timezone-aware

async def create_task(conn, workspace_id: int, task: taskCreate):
    # Handle defaults in Python, not in SQL
    status = task.status or "pending"
    priority = task.priority_level or "low"

    # Validate enum values
    valid_status = {"pending", "in_progress", "completed"}
    valid_priority = {"low", "medium", "high"}

    if status not in valid_status:
        raise ValueError(f"Invalid status: {status}. Must be one of {valid_status}")

    if priority not in valid_priority:
        raise ValueError(f"Invalid priority: {priority}. Must be one of {valid_priority}")

    query = """
        INSERT INTO tasks 
        (workspace_id, title, description, deadline, status, priority_level, created_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING task_id, workspace_id, title, description, deadline, status, priority_level, created_by, created_at;
    """

    row = await conn.fetchrow(
        query,
        workspace_id,
        task.title,
        task.description,
        task.deadline,
        status,     # safe, validated
        priority,   # safe, validated
        task.created_by,
    )
    return dict(row)

async def get_task(conn, workspace_id: int, task_id: int):  # Get specific task by ID
    query = """
        SELECT * 
        FROM tasks 
        WHERE workspace_id = $1 AND task_id = $2
    """
    row = await conn.fetchrow(query, workspace_id, task_id)
    return dict(row) if row else None


async def get_tasks_by_workspace(conn, workspace_id: int):  # Get tasks from that workspace
    query = """
        SELECT * 
        FROM tasks 
        WHERE workspace_id = $1
        ORDER BY created_at DESC
    """
    rows = await conn.fetch(query, workspace_id)
    return [dict(r) for r in rows]

from datetime import datetime, timezone

from datetime import datetime, timezone

from datetime import datetime, timezone

async def update_task(conn, task_id: int, workspace_id: int, task_update: taskUpdate):
    query = """
        UPDATE tasks
        SET title = COALESCE($1, title),
            description = COALESCE($2, description),
            status = COALESCE($3, status)
        WHERE task_id = $4 AND workspace_id = $5
        RETURNING *;
    """
    row = await conn.fetchrow(
        query,
        task_update.title,       # ✅ works because it’s still a Pydantic model
        task_update.description,
        task_update.status,
        task_id,
        workspace_id,
    )
    return dict(row) if row else None

async def delete_task(conn, workspace_id: int, task_id: int):
    query = "DELETE FROM tasks WHERE task_id=$1 AND workspace_id=$2 RETURNING *;"
    row = await conn.fetchrow(query, task_id, workspace_id)
    return dict(row) if row else None

