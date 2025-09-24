from ...task.schemas.TaskComment_schema import TaskCommentCreate, TaskCommentUpdate, TaskCommentOut
from ...utils.decorators import db_error_handler


# Comment on a task
@db_error_handler
async def create_taskcomment(conn, task_id: int, taskcomment: TaskCommentCreate):
    query = """
            INSERT INTO task_comments (task_id, content, sender_id)
            VALUES ($1, $2, $3)
            RETURNING comment_id, task_id, content, created_at, sender_id;
        """
    row = await conn.fetchrow(query, task_id, taskcomment.content, taskcomment.sender_id,)
    
    if not row:
        return None
    comment_id = row["comment_id"]

    attachments = []
    if taskcomment.attachments:
        attachment_query = """
            INSERT INTO comment_attachments
            (comment_id, task_id, name, file_size, file_type, file_url, uploaded_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *;
        """

    for attachment in taskcomment.attachments:
        att_row = await conn.fetchrow(
            attachment_query,
            comment_id,
            task_id,
            attachment.name,
            attachment.file_size,
            attachment.file_type,
            attachment.file_url,
            attachment.uploaded_by,
        )
        attachments.append(dict(att_row))
    return {
        "content": row["content"],
        "sender_id": row["sender_id"],
        "attachments": attachments
}

# View comments in a task
@db_error_handler
async def get_taskcomment(conn, task_id: int):
    query = """
        SELECT
            tc.comment_id,
            tc.task_id,
            tc.content,
            tc.sender_id,
            tc.created_at,
            u.profile_picture,
            (u.first_name || ' ' || u.last_name) AS sender_name,
            a.comment_attachment_id,
            a.name,
            a.file_size,
            a.file_type,
            a.file_url,
            a.uploaded_by,
            a.uploaded_at
        FROM task_comments tc
        LEFT JOIN users u ON u.user_id = tc.sender_id
        LEFT JOIN comment_attachments a ON a.comment_id = tc.comment_id
        WHERE tc.task_id = $1
        ORDER BY tc.created_at ASC;
    """
    rows = await conn.fetch(query, task_id)
    comments = {}

    for r in rows:
        cid = r["comment_id"]
        if cid not in comments:
            comments[cid] = {
                "comment_id": r["comment_id"],
                "task_id": r["task_id"],
                "content": r["content"],
                "sender_id": r["sender_id"],
                "created_at": r["created_at"],
                "profile_picture": r["profile_picture"],
                "sender_name": r["sender_name"],
                "attachments": []
            }

        if r["comment_attachment_id"]:
            comments[cid]["attachments"].append({
                "comment_attachment_id": r["comment_attachment_id"],
                "comment_id": r["comment_id"],
                "task_id": r["task_id"],
                "name": r["name"],           
                "file_size": r["file_size"],
                "file_type": r["file_type"],
                "file_url": r["file_url"],
                "uploaded_by": r["uploaded_by"],
                "uploaded_at": r["uploaded_at"] 
            })

    return list(comments.values())



# Editing a comment
@db_error_handler
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
@db_error_handler
async def delete_taskcomment(conn, comment_id: int, task_id: int):
    query = "DELETE FROM task_comments WHERE comment_id = $1 AND task_id = $2 RETURNING *;"
    row = await conn.fetchrow(query, comment_id, task_id)
    return dict(row) if row else None