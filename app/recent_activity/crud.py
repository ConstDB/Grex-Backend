from datetime import date
from app.utils.decorators import db_error_handler

@db_error_handler
async def add_activity_db(conn, workspace_id: int,
                                task_log_id: int | None, 
                                content: str):
    query = """
            INSERT INTO recent_activities(workspace_id, task_log_id, content)
            VALUES ($1, $2, $3)
            RETURNING activity_id
            """
    row = await conn.fetchrow(query, workspace_id,
                                task_log_id, 
                                content)
    return dict(row)

@db_error_handler
async def get_activity_db(conn, workspace_id: int):
    query = """
            SELECT *
            FROM recent_activities
            WHERE workspace_id = $1
            ORDER BY activity_id DESC
            LIMIT 8
        """
    rows = await conn.fetch(query, workspace_id)
    return [dict(r) for r in rows]