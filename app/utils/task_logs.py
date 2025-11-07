from datetime import datetime
from app.utils.decorators import db_error_handler
from ..ai_assistant.vectorstore.task_vector_store import ProcessTaskLog

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
    
    await process.insert_data(dict_row["task_log_id"], workspace_id, content)
    return dict_row
