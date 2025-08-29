from app.task.schemas.SubTasks_schema import SubTasksCreate, SubTasksPatch
from datetime import datetime
from app.utils.decorators import db_error_handler
from app.utils.task_logs import log_task_action

now = datetime.now()    

# Create a subtask
@db_error_handler
async def create_subtask(conn, task_id: int, subtask: SubTasksCreate):
    query = """
        INSERT INTO subtasks (task_id, description, is_done, created_at)
        VALUES ($1, $2, $3, $4)
        RETURNING subtask_id, task_id, description, is_done, created_at
    """
    row = await conn.fetchrow(query, task_id, subtask.description, subtask.is_done, now)

    if row:
        # Get workspace_id from the task
        task_row = await conn.fetchrow("SELECT workspace_id FROM tasks WHERE task_id=$1", task_id)
        workspace_id = task_row["workspace_id"] if task_row else None

        # Log creation in task_logs as Leader
        if workspace_id:
            content = (
                f"Leader created a subtask with subtask_id: {row['subtask_id']} for task {task_id}: "
                f"description='{row['description']}', is_done={row['is_done']}, created_at={row['created_at']}"
            )
            await log_task_action(conn, workspace_id, content)

        return dict(row)

    return None

# Get specific subtask by subtask_id
# async def get_subtask(conn, task_id: int, subtask_id: int):
#     query = """
#             SELECT *
#             FROM subtasks
#             WHERE task_id = $1 AND subtask_id = $2
#         """
#     row = await conn.fetchrow(query, task_id, subtask_id)
#     return dict(row) if row else None


# get all subtask from specific task
@db_error_handler
async def get_subtasks_by_task(conn, task_id: int):
    query = """
            SELECT *
            FROM subtasks
            WHERE task_id = $1
        """
    rows = await conn.fetch(query, task_id)
    return [dict(r) for r in rows]

# Patch task in workspace
# @db_error_handler
# async def patch_subtask(conn, task_id: int, subtask_id: int, subtask_update: SubTasksPatch):
#     updates = []
#     values = []
#     idx = 1  # parameter placeholder counter

#     if subtask_update.description is not None:
#         updates.append(f"description = ${idx}")
#         values.append(subtask_update.description)
#         idx += 1

#     if subtask_update.is_done is not None:
#         updates.append(f"is_done = ${idx}")
#         values.append(subtask_update.is_done)
#         idx += 1

#     if not updates:
#         return None  # nothing to update

#     query = f"""
#             UPDATE subtasks
#                 SET {", ".join(updates)}
#             WHERE subtask_id = ${idx} AND task_id = ${idx+1}
#             RETURNING {", ".join([u.split(" = ")[0] for u in updates])};
#         """
#     values.extend([subtask_id, task_id])

#     row = await conn.fetchrow(query, *values)
#     return dict(row) if row else None

# PUT to update whether subtask is done or not
@db_error_handler
async def update_subtask_status(conn, task_id: int, subtask_id: int, subtask_update: SubTasksPatch):
    query = f"UPDATE subtasks SET is_done = COALESCE($3, is_done) WHERE task_id = $1 AND subtask_id = $2 RETURNING *;"
    row = await conn.fetchrow(query, task_id, subtask_id, subtask_update.is_done)
    return dict(row)
    # if not row:
    #     return None
    # content = (
    #     f"A member has finished a subtask_id: {subtask_id} to {subtask_update.is_done}"
    # )
    # await log_task_action(conn, task_id, content)

# Delete a subtask
@db_error_handler
async def delete_subtask(conn, task_id:int, subtask_id: int):
    query = "DELETE FROM subtasks WHERE task_id=$1 AND subtask_id=$2 RETURNING *;"
    row = await conn.fetchrow(query, task_id, subtask_id)

    if not row:
        return None
    
    content = (
        f"A workspace Leader deleted subtask_id: {row['subtask_id']}"
    )
    await log_task_action(conn, task_id, content)
    return dict(row)
