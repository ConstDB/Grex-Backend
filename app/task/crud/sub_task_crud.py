from app.task.schemas.SubTasks_schema import SubTasksCreate, SubTasksUpdate, SubTasksDelete
from datetime import datetime, timezone

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

# Update a subtask
async def update_subtask(conn, task_id: int, subtask_id: int, subtask_update:SubTasksUpdate):
    query = """
            UPDATE subtasks
            SET description = COALESCE($1, description),
                is_done = COALESCE($2, is_done)
            WHERE subtask_id = $3 AND task_id = $4
            RETURNING *;
        """
    row = await conn.fetchrow(
        query,
        subtask_update.description,
        subtask_update.is_done,
        subtask_id,
        task_id
    )
    return dict(row) if row else None

# Delete a subtask
async def delete_subtask(conn, task_id:int, subtask_id: int, subtask_delete: SubTasksDelete):
    query = "DELETE FROM subtasks WHERE subtask_id=$1 AND task_id=$2 RETURNING *;"
    row = await conn.fetchrow(query, subtask_id, task_id)
    return dict(row) if row else None
