from fastapi import APIRouter, Depends, HTTPException
from ...deps import get_db_connection
from app.task.crud import sub_task_crud
from app.task.schemas.SubTasks_schema import SubTasksCreate, SubTasksPatch, SubTasksDelete
import asyncpg

router = APIRouter()

# Router for creating subtask
@router.post("/{task_id}")
async def create_subtask(task_id: int, subtask: SubTasksCreate, conn: asyncpg.Connection = Depends (get_db_connection)):
    created = await sub_task_crud.create_subtask(conn, task_id, subtask)
    if not created:
        raise HTTPException(status_code=400, detail="Failed to create subtask")
    return{"status": "success", "data": created}

# Router for getting specific subtask by task_id and subtask_id
@router.get("/{task_id}/{subtasK_id}")
async def get_subtask(task_id:int, subtask_id: int, conn: asyncpg.Connection = Depends (get_db_connection)):
    subtask = await sub_task_crud.get_subtask(conn, task_id, subtask_id)
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return{"status": "success", "data": subtask}

# Router for getting all subtask in task_id
@router.get("/{task_id}")
async def get_subtasks_by_task(task_id: int, conn: asyncpg.Connection = Depends(get_db_connection)):
    subtask = await sub_task_crud.get_subtasks_by_task(conn, task_id)
    return{"status": "success", "data": subtask}

# Router for patching a subtask
@router.patch("/{task_id}/{subtask_id}")
async def subtask_patch(
    task_id: int,
    subtask_id: int,
    subtask_patch: SubTasksPatch,
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    updated = await sub_task_crud.patch_subtask(conn, task_id, subtask_id, subtask_patch)
    if not updated:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return updated

# Router for deleting a subtask
@router.delete("/{task_id}/{subtask_id}")
async def delete_subtask(task_id: int, subtask_id: int, subtask_delete: SubTasksDelete, conn: asyncpg.Connection = Depends(get_db_connection)):
    deleted = await sub_task_crud.delete_subtask(conn, task_id, subtask_id, subtask_delete)
    if not deleted:
        raise HTTPException(status_code=404, detail="Subtask not found or failed to delete")
    return{"status": "success", "message": "Subtask Deleted"}
