from datetime import datetime, timezone
import asyncpg

async def is_overdue(deadline: datetime, status: str) -> bool:
    """
    Check if a task is overdue.
    Returns True if the deadline has passed and task is not done.
    """

    if isinstance(deadline, str):
        deadline_dt = datetime.fromisoformat(deadline.replace(" ", "T"))
    else:
        deadline_dt = deadline

    if deadline_dt.tzinfo is None:
        deadline_dt = deadline_dt.replace(tzinfo=timezone.utc)

    if status == "done" or status == "overdue":
        return False

    return deadline_dt < datetime.now(timezone.utc)


async def set_status_to_overdue(task_id: int, conn: asyncpg.Connection):

    # update status to overdue
    return await conn.fetchrow(
        """
                
        WITH updated AS (
            UPDATE tasks t
            SET status='overdue'
            WHERE t.task_id = $1
            RETURNING *
        )
        SELECT 
            u.task_id,
            u.workspace_id,
            u.category_id,
            c.name AS category,
            u.subject,
            u.title,
            u.description,
            u.deadline,
            u.status,
            u.priority_level,
            u.start_date,
            u.created_by,
            u.created_at,
            u.marked_done_at
        FROM updated u
        LEFT JOIN categories c ON u.category_id = c.category_id;  
        """,
        task_id
    )
