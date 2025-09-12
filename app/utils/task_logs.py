from datetime import datetime
from app.utils.decorators import db_error_handler
from ..ai.task_logs_vdb import ProcessTaskLog

process = ProcessTaskLog()
@db_error_handler
async def log_task_action(conn, workspace_id: int, content: str):
    query = """
        INSERT INTO task_logs(workspace_id, context)
        VALUES ($1, $2)
        RETURNING task_log_id;
    """
    row = await conn.fetchrow(query, workspace_id, content)
    dict_row = dict(row)
    
    process.insert_data(dict_row["task_log_id"], workspace_id, content)
    return dict_row
