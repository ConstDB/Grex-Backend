# app/api/task/crud/task_crud.py

from app.task.schemas.Tasks_schema import TaskCreate, TaskPatch
from fastapi import HTTPException
from datetime import datetime, timezone
from app.utils.decorators import db_error_handler
from app.utils.task_logs import log_task_action

now = datetime.now(timezone.utc)

# Create task in workspace
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
        (workspace_id, title, subject, description, deadline, status, priority_level, created_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING task_id, workspace_id, title, subject, description, deadline, status, priority_level, created_by, created_at;
    """
    row = await conn.fetchrow(query, workspace_id, task.title, task.subject, task.description, task.deadline, status, priority, task.created_by)
    task_id = row['task_id']

    # Log the creation
    content = (
        f"Leader {task.created_by} created task '{task.title}' "
        f"(task_id: {task_id}) with description '{task.description}', deadline: {task.deadline.isoformat()}."
    )
    await log_task_action(conn, workspace_id, content)

    return dict(row)

    
# async def get_task(conn, workspace_id: int, task_id: int):
#     try:
#         # Get main task
#         task_query = """
#             SELECT *
#             FROM tasks
#             WHERE workspace_id = $1 AND task_id = $2
#         """
#         task_row = await conn.fetchrow(task_query, workspace_id, task_id)
#         if not task_row:
#             return None
#         task_dict = dict(task_row)

#         # Get subtasks for this task
#         try:
#             subtasks_rows = await conn.fetch("SELECT * FROM subtasks WHERE task_id = $1", task_id)
#             task_dict["subtasks"] = [dict(r) for r in subtasks_rows]
#         except Exception as e:
#             print("Error fetching subtasks:", e)
#             task_dict["subtasks"] = []

#         # Get comments for this task
#         try:
#             comments_rows = await conn.fetch("SELECT * FROM task_comments WHERE task_id = $1", task_id)
#             task_dict["comments"] = [dict(r) for r in comments_rows]
#         except Exception as e:
#             print("Error fetching comments:", e)
#             task_dict["comments"] = []

#         # Get attachments for this task
#         try:
#             attachments_rows = await conn.fetch("SELECT * FROM task_attachments WHERE task_id = $1", task_id)
#             task_dict["attachments"] = [dict(r) for r in attachments_rows]
#         except Exception as e:
#             print("Error fetching attachments:", e)
#             task_dict["attachments"] = []

#         # Get assignments for this task
#         try:
#             assignments_rows = await conn.fetch("SELECT * FROM task_assignments WHERE task_id = $1", task_id)
#             task_dict["assignments"] = [dict(r) for r in assignments_rows]
#         except Exception as e:
#             print("Error fetching assignments:", e)
#             task_dict["assignments"] = []

#         return task_dict

#     except Exception as e:
#         print("Main get_task error:", e)
#         return None

@db_error_handler
async def get_task(conn, workspace_id: int, task_id: int):
    query = "SELECT * FROM tasks WHERE workspace_id = $1 AND task_id = $2"
    row = await conn.fetchrow(query, workspace_id, task_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found in workspace {workspace_id}")
    return dict(row)

# Get all tasks from that workspace
@db_error_handler
async def get_tasks_by_workspace(conn, workspace_id: int): 
    query = "SELECT * FROM tasks WHERE workspace_id = $1 ORDER BY created_at DESC"
    rows = await conn.fetch(query, workspace_id)
    return [dict(row.items()) for row in rows] if rows else []

    # results = []
    # for task in rows: 
    #     task_id = task["task_id"]

    #     rows = await conn.fetch(query, workspace_id)
    #     subtasks = await conn.fetch("SELECT * FROM  subtasks WHERE task_id = $1", task_id)
    #     comments = await conn.fetch("SELECT * FROM task_comments WHERE task_id = $1", task_id)
    #     assignments = await conn.fetch("SELECT * FROM task_assignments WHERE task_id = $1", task_id)
    #     attachments = await conn.fetch("SELECT * FROM task_attachments WHERE task_id = $1", task_id)

    #     results.append({
    #         **dict(task),
    #         "subtasks": [dict(s) for s in subtasks],
    #         "comments": [dict(s) for s in comments],
    #         "assignments": [dict(a) for a in assignments],
    #         "attachments": [dict(att) for att in attachments], 
    #     })
    # return results

# Patch task in workspace
@db_error_handler
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

    if patch_task.marked_done_at is not None:
        updates.append(f"marked_done_at = ${idx}")
        values.append(patch_task.marked_done_at)
        idx += 1

    if not updates:
        return None
    
    updated_fields = []
    
    if patch_task.title is not None:
        updated_fields.append(f"title='{patch_task.title}'")
    if patch_task.subject is not None:
        updated_fields.append(f"subject='{patch_task.subject}'")
    if patch_task.description is not None:
        updated_fields.append(f"description='{patch_task.description}'")
    if patch_task.deadline is not None:
        updated_fields.append(f"deadline={patch_task.deadline.isoformat()}")
    if patch_task.status is not None:
        updated_fields.append(f"status='{patch_task.status}'")
    if patch_task.priority_level is not None:
        updated_fields.append(f"priority_level='{patch_task.priority_level}'")
    if patch_task.marked_done_at is not None:
        updated_fields.append(f"marked_done_at={patch_task.marked_done_at.isoformat()}")
    
    query = f"""
            UPDATE tasks
                SET {", ".join(updates)}
            WHERE task_id = ${idx} AND workspace_id = ${idx+1}
            RETURNING *;
            """
    values.extend([task_id, workspace_id])

    row = await conn.fetchrow(query, *values)
    
    if row:
        # Log the patch action
        content = (
            f"Leader {patch_task.updated_by} patched task_id {task_id}: "
            + ", ".join(updated_fields)
        )
        await log_task_action(conn, workspace_id, content)
        return dict(row)
    return None

# Delete task in workspace
@db_error_handler
async def delete_task(conn, workspace_id: int, task_id: int):
    query = "DELETE FROM tasks WHERE task_id=$1 AND workspace_id=$2 RETURNING *;"
    row = await conn.fetchrow(query, task_id, workspace_id)
    return dict(row) if row else None
    