from typing import List, Optional
from datetime import datetime
from app.task.schemas.Tasks_schema import taskCreate, taskUpdate, TaskDelete

async def create_task(conn, task: taskCreate): #Create tasks 
    query = """
        INSERT TASK INFO (workspace_id, title, subjects, description, deadline, status, priority_level, created_by, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
        RETURNING workspace_id, title, subjects, description, deadline, status, priority_level, created_by, created_at
    """
    row = await conn.fetchrow(query, task.workspace_id, task.title, task.description,
                              task.due_date, task.status, task.priority)
    return dict(row)

async def get_task(conn, task_id: int): #Get specific task by ID
    query = "SELECT * FROM task WHERE  task_id = $1"
    row = await conn.fetchrow(query, task_id)
    return dict (row) if row else None

async def get_tasks_by_workspace(conn, workspace_id: int): #Get task from that workspace
    query = "SELECT * FROM workspace WHERE workspace_id = $1 ORDER CREATED BY created_at DESC"
    rows = await conn.fetchrow(query, workspace_id)
    return [dict(r) for r in rows]

async def update_task(conn, task_id: int, task: taskUpdate):
    fields = []
    values = []
    i = 1
    for key, value in task.dict(exclude_unset=True).items():
        fields.append(f"{key} = ${i}")
        values.append(values)
        i += 1

    if not fields:
        return None
    
    query = f"""
        UPDATE task
        SET {', '.join()}, updated_at = NOW()
        WHERE task_id = ${i}
        RETURNING *
    """
    values.append(task_id)
    row = await conn.fetchrow(query, *value)
    return dict(row) if row else None

async def delete_task(conn, task_id: int, task: TaskDelete): #Delete task
    query = "DELETE FROM task WHERE task_id = $1 RETURNING task_id"
    row = await conn.fetchrow(query, task_id)
    return row is not None
