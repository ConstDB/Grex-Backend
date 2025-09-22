from datetime import datetime, timezone
import asyncpg

async def is_overdue(deadline: datetime, status: str) -> bool:
    """
    Check if a task is overdue.
    Returns True if the deadline has passed and task is not done.
    """
    if status == "done":
        return False

    if isinstance(deadline, str):
        deadline_dt = datetime.fromisoformat(deadline.replace(" ", "T"))
    else:
        deadline_dt = deadline

    return deadline_dt < datetime.now(timezone.utc)


async def set_status_to_overdue(workspace_id: int, task_id: int, conn: asyncpg.Connection):
    # fetch the task deadline and status
    task = await conn.fetchrow(
        "SELECT deadline, status, marked_done_at FROM tasks WHERE workspace_id=$1 AND task_id=$2",
        workspace_id, task_id
    )
    if not task:
        return

    # if done then skip
    if task["status"] == "done":
        return

    deadline = task["deadline"]
    if deadline and deadline < datetime.now(timezone.utc):
        # update status to overdue
        await conn.execute(
            "UPDATE tasks SET status='overdue' WHERE workspace_id=$1 AND task_id=$2",
            workspace_id, task_id
        )
