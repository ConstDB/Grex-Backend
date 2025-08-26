from app.task.schemas.SubTasks_schema import SubTasksCreate, SubTasksPatch, SubTasksDelete
from datetime import datetime

now = datetime.now()    

# Create a subtask
async def create_subtask(conn, task_id: int, subtask: SubTasksCreate):
    query = """
            INSERT INTO subtasks (task_id, description, is_done, created_at)
            VALUES ($1, $2, $3, $4)
            RETURNING subtask_id, task_id, description, is_done, created_at
        """
    row = await conn.fetchrow(query, task_id, subtask.description, subtask.is_done, now)
    return dict(row)

# Get specific subtask by subtask_id
async def get_subtask(conn, task_id: int, subtask_id: int):
    query = """
            SELECT *
            FROM subtasks
            WHERE task_id = $1 AND subtask_id = $2
        """
    row = await conn.fetchrow(query, task_id, subtask_id)
    return dict(row) if row else None

# get all subtask from specific task
async def get_subtasks_by_task(conn, task_id: int):
    query = """
            SELECT *
            FROM subtasks
            WHERE task_id = $1
        """
    rows = await conn.fetch(query, task_id)
    return [dict(r) for r in rows]

# Patch task in workspace
async def patch_subtask(conn, task_id: int, subtask_id: int, subtask_update: SubTasksPatch):
    updates = []
    values = []
    idx = 1  # parameter placeholder counter

    if subtask_update.description is not None:
        updates.append(f"description = ${idx}")
        values.append(subtask_update.description)
        idx += 1

    if subtask_update.is_done is not None:
        updates.append(f"is_done = ${idx}")
        values.append(subtask_update.is_done)
        idx += 1

    if not updates:
        return None  # nothing to update

    query = f"""
            UPDATE subtasks
                SET {", ".join(updates)}
            WHERE subtask_id = ${idx} AND task_id = ${idx+1}
            RETURNING {", ".join([u.split(" = ")[0] for u in updates])};
        """
    values.extend([subtask_id, task_id])

    row = await conn.fetchrow(query, *values)
    return dict(row) if row else None

# Delete a subtask
async def delete_subtask(conn, task_id:int, subtask_id: int, subtask_delete: SubTasksDelete):
    query = "DELETE FROM subtasks WHERE subtask_id=$1 AND task_id=$2 RETURNING *;"
    row = await conn.fetchrow(query, subtask_id, task_id)
    return dict(row) if row else None
