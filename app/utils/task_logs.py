from datetime import datetime
from app.utils.decorators import db_error_handler

@db_error_handler
async def log_task_action(conn, workspace_id: int, content: str):
    query = """
        INSERT INTO task_logs(workspace_id, context)
        VALUES ($1, $2)
        RETURNING task_log_id;
    """
    row = await conn.fetchrow(query, workspace_id, content)
    return dict(row)