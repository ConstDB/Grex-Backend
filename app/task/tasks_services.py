from datetime import datetime, timezone
from .schemas.Tasks_schema import TaskPatch
from .crud.task_crud import patch_task
import asyncio
import asyncpg


async def is_overdue(deadline: datetime):

    deadline_dt = datetime.fromisoformat(deadline.replace(" ", "T"))
    if deadline_dt < datetime.now(timezone.utc):

        return True
    return False

# asyncio.run(is_overdue("2025-09-22 10:57:45.43+00"))

async def set_status_to_overdue(workspace_id: int, task_id:int, conn: asyncpg.Connection):
    payload = {
        "status":"overdue"
    }

    payload = TaskPatch(**payload)

    
