from app.task.schemas.TaskComment_schema import TaskCommentCreate, TaskCommentDelete, TaskCommentUpdate
from datetime import datetime

# Comment on a task
from datetime import datetime

async def create_taskcomment(conn, task_id: int, taskcomment: TaskCommentCreate):
    created_at = datetime.now()
    query = """
            INSERT INTO task_comments (task_id, content, created_at, sender_id)
            VALUES ($1, $2, $3, $4)
            RETURNING comment_id, task_id, content, created_at, sender_id;
        """
    row = await conn.fetchrow(query,
                              task_id,
                              taskcomment.content,
                              created_at,
                              taskcomment.sender_id,
                              )
    return dict(row)

# View comments in a task
async def get_taskcomment(conn, task_id: int):
    query = """
        SELECT *
        FROM task_comments
        WHERE task_id = $1
        """
    rows = await conn.fetch(query, task_id)
    return [dict(r) for r in rows]

# Editing a comment
async def update_taskcomment(conn, task_id: int, comment_id: int, taskcomment: TaskCommentUpdate):
    query = """
        UPDATE task_comments
        SET content = COALESCE($1, content)
        WHERE comment_id = $2 AND task_id = $3
        RETURNING *;
        """
    row = await conn.fetchrow(query, taskcomment.content, comment_id, task_id)
    return dict(row) if row else None

# Delete comment from task
async def delete_taskcomment(conn, comment_id: int, task_id: int):
    query = "DELETE FROM task_comments WHERE comment_id = $1 AND task_id = $2 RETURNING *;"
    row = await conn.fetchrow(query, comment_id, task_id)
    return dict(row) if row else None