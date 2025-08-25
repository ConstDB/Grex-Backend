# app/api/task/crud/task_crud.py

from app.task.schemas.Tasks_schema import TaskCreate, TaskPatch
from datetime import datetime, timezone

now = datetime.now(timezone.utc)  

# Create task in workspace
async def create_task(conn, workspace_id: int, task: TaskCreate):
    status = task.status or "pending"
    priority = task.priority_level or "low"

    valid_status = {"pending", "done", "overdue"}
    valid_priority = {"low", "medium", "high"}

    if status not in valid_status:
        raise ValueError(f"Invalid status: {status}. Must be one of {valid_status}")

    if priority not in valid_priority:
        raise ValueError(f"Invalid priority: {priority}. Must be one of {valid_priority}")

    query = """
        INSERT INTO tasks 
        (workspace_id, title, subject, description, deadline, status, priority_level, created_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING task_id, workspace_id, title, subject, description, deadline, status, priority_level, created_by, created_at;
    """

    row = await conn.fetchrow(
        query,
        workspace_id,
        task.title,
        task.subject,
        task.description,
        task.deadline,
        status,     
        priority,  
        task.created_by,
    )
    return dict(row)

# Get specific task by ID
async def get_task(conn, workspace_id: int, task_id: int):  
    query = """
        SELECT * 
        FROM tasks 
        WHERE workspace_id = $1 AND task_id = $2
    """
    row = await conn.fetchrow(query, workspace_id, task_id)
    return dict(row) if row else None

# Get tasks from that workspace
async def get_tasks_by_workspace(conn, workspace_id: int): 
    query = """
        SELECT * 
        FROM tasks 
        WHERE workspace_id = $1
        ORDER BY created_at DESC
    """
    rows = await conn.fetch(query, workspace_id)
    return [dict(r) for r in rows]

# Patch task in workspace
async def patch_task(conn, task_id: int, workspace_id: int, patch_task: TaskPatch):
    updates = []
    values = []
    idx = 1
     
    if patch_task.title is not None:
        updates.append(f"title = ${idx}")
        values.append(patch_task.title)
        idx += 1

    if patch_task.subject is not None:
        updates.append(f"subject = ${idx}")
        values.append(patch_task.subject)
        idx += 1

    if patch_task.description is not None:
        updates.append(f"description = ${idx}")
        values.append(patch_task.description)
        idx += 1

    if patch_task.deadline is not None:
        updates.append(f"deadline = ${idx}")
        values.append(patch_task.deadline)
        idx += 1

    if patch_task.status is not None:
        updates.append(f"status = ${idx}")
        values.append(patch_task.status)
        idx += 1

    if patch_task.priority_level is not None:
        updates.append(f"priority_level = ${idx}")
        values.append(patch_task.priority_level)
        idx += 1

    if not updates:
        return None
    
    query = f"""
            UPDATE tasks
                SET {", ".join(updates)}
            WHERE task_id = ${idx} AND workspace_id = ${idx+1}
            RETURNING *;
        """
    values.extend([task_id, workspace_id])

    row = await conn.fetchrow(query, *values)
    return dict(row) if row else None


    # query = """
    #     UPDATE tasks
    #     SET title = COALESCE($1, title),
    #         subject = COALESCE($2, subject),
    #         description = COALESCE($3, description),
    #         status = COALESCE($4, status)
    #     WHERE task_id = $5 AND workspace_id = $6
    #     RETURNING *;
    # """
    # row = await conn.fetchrow(
    #     query,
    #     task_update.title,
    #     task_update.subject,       
    #     task_update.description,
    #     task_update.status,
    #     task_id,
    #     workspace_id,
    # )
    # return dict(row) if row else None

async def delete_task(conn, workspace_id: int, task_id: int): 
    query = "DELETE FROM tasks WHERE task_id=$1 AND workspace_id=$2 RETURNING *;"
    row = await conn.fetchrow(query, task_id, workspace_id)
    return dict(row) if row else None

