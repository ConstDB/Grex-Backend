# app/api/task/crud/task_attachment_crud.py

from datetime import datetime
from app.task.schemas.TaskAttachment_schema import TaskAttachmentCreate, TaskAttachmentDelete
from app.core.decorators import db_error_handler

# Create a task attachment
@db_error_handler
async def create_attachment(conn, task_id: int, attachment: TaskAttachmentCreate):
    # Validate task exists
    task = await conn.fetchrow("SELECT task_id FROM tasks WHERE task_id=$1", task_id)
    if not task:
        raise ValueError(f"Task with id {task_id} does not exist")

    query = """
        INSERT INTO task_attachments
        (task_id, uploaded_by, file_url, file_type, file_size_mb, uploaded_at)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING attachment_id, task_id, uploaded_by, file_url, file_type, file_size_mb, uploaded_at;
    """
    row = await conn.fetchrow(
        query,
        task_id,
        attachment.uploaded_by,
        attachment.file_url,
        attachment.file_type,
        attachment.file_size_mb,
        datetime.now()
    )
    return dict(row)

# Get all attachments for a task
@db_error_handler
async def get_attachments_by_task(conn, task_id: int):
    query = """
        SELECT * FROM task_attachments
        WHERE task_id = $1
        ORDER BY uploaded_at DESC
    """
    rows = await conn.fetch(query, task_id)
    if not rows:
        raise ValueError(f"Task with id {task_id} does not exist")
    return [dict(r) for r in rows]  


# Delete a task attachment
@db_error_handler
async def delete_attachment(conn, attachment: TaskAttachmentDelete):
    query = """
        DELETE FROM task_attachments
        WHERE attachment_id = $1 AND task_id = $2
        RETURNING *;
    """
    row = await conn.fetchrow(query, attachment.attachment_id, attachment.task_id)
    return dict(row) if row else None
