# app/api/task/crud/task_crud.py

from ...task.schemas.Tasks_schema import TaskCreate, TaskPatch, TaskCreateOut
from fastapi import HTTPException
from datetime import datetime, timezone
from ...utils.decorators import db_error_handler
from ...utils.task_logs import log_task_action


now = datetime.now(timezone.utc)


@db_error_handler
async def create_task(conn, workspace_id: int, task: TaskCreate):
    status = task.status or "pending"
    priority = task.priority_level or "low"

    valid_status = {"pending", "done", "overdue"}
    valid_priority = {"low", "medium", "high"}

    if status not in valid_status:
        raise ValueError(f"Invalid status: {status}. Must be one of {valid_status}")
    if priority not in valid_priority:
        raise ValueError(f"Invalid priority: {priority}. Must be one of {valid_priority}")

    user_exists = await conn.fetchrow(
        "SELECT user_id FROM users WHERE user_id = $1", task.created_by
    )
    if not user_exists:
        raise HTTPException(status_code=404, detail=f"User with id {task.created_by} does not exist")

    query = """
        INSERT INTO tasks 
        (workspace_id, title, subject, description, deadline, status, priority_level, start_date, created_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING task_id, workspace_id, title, subject, description, deadline, status, priority_level, start_date, created_by, created_at;
    """
    row = await conn.fetchrow(query, 
                              workspace_id, 
                              task.title, 
                              task.subject, 
                              task.description, 
                              task.deadline, 
                              status, 
                              priority, 
                              task.start_date, 
                              task.created_by)
    task_id = row['task_id']

    # Log the creation
    content = (
        f"Leader {task.created_by} created task '{task.title}' "
        f"(task_id: {task_id}) with description '{task.description}', deadline: {task.deadline.isoformat()}."
    )
    await log_task_action(conn, workspace_id, content)

    return TaskCreateOut(**dict(row))


@db_error_handler
async def get_task(conn, workspace_id: int, task_id: int):
    query = "SELECT * FROM tasks WHERE workspace_id = $1 AND task_id = $2"
    row = await conn.fetchrow(query, workspace_id, task_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found in workspace {workspace_id}")
    return dict(row)


@db_error_handler
async def get_tasks_by_workspace(conn, workspace_id: int): 
    query = "SELECT * FROM tasks WHERE workspace_id = $1 ORDER BY created_at DESC"
    rows = await conn.fetch(query, workspace_id)
    return [dict(row.items()) for row in rows] if rows else []


@db_error_handler
async def patch_task(
    conn,
    workspace_id: int,
    task_id: int,
    patch_task: TaskPatch
):
    # Build dict only from explicitly provided fields
    update_data = patch_task.model_dump(exclude_unset=True)

    if not update_data:
        return {"status": "no changes"}

    # Extract updated_by separately so it's not included in SQL
    updated_by = update_data.pop("updated_by", None)

    if not update_data:
        return {"status": "no changes"}

    # Fetch current task row before updating (for comparison)
    current_task = await conn.fetchrow(
        "SELECT * FROM tasks WHERE task_id=$1 AND workspace_id=$2",
        task_id, workspace_id
    )

    if not current_task:
        return None

    # Determine which fields are actually changing
    changed_fields = {
        field: value
        for field, value in update_data.items()
        if value != current_task[field]
    }

    if not changed_fields:
        return {"status": "no actual changes"}

    # Build SQL update only with changed fields
    set_clause = ", ".join([f"{key} = ${i+1}" for i, key in enumerate(changed_fields.keys())])
    values = list(changed_fields.values())

    query = f"""
        UPDATE tasks
        SET {set_clause}
        WHERE task_id = ${len(values)+1} AND workspace_id = ${len(values)+2}
        RETURNING *;
    """
    row = await conn.fetchrow(query, *values, task_id, workspace_id)

    if not row:
        return None

    # Log only changed fields
    changes = ", ".join(
        f"{field} changed from '{current_task[field]}' to '{value}'"
        for field, value in changed_fields.items()
    )

    content = f"Leader {updated_by} patched task_id {task_id}. Changes: {changes}"
    await log_task_action(conn, workspace_id, content)

    return dict(row)


@db_error_handler
async def delete_task(conn, workspace_id: int, task_id: int):
    query = "DELETE FROM tasks WHERE task_id=$1 AND workspace_id=$2 RETURNING *;"
    row = await conn.fetchrow(query, task_id, workspace_id)

    if not row:
        return None  # task not found
    
    content = (
        f"A workspace Leader deleted task_id: {row['task_id']}"
    )
    await log_task_action(conn, workspace_id, content)
    return dict(row)