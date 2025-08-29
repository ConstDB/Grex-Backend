
# app/api/routes/task_router.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List
import asyncpg
from ...deps import get_db_connection  
from ...users.auth import get_current_user
from app.task.schemas.Tasks_schema import TaskCreate, TaskPatch, TaskAllOut
from app.task.crud import task_crud
from app.utils.decorators import db_error_handler

router = APIRouter()

# Create a Task
@router.post("/{workspace_id}", response_model=TaskCreate)
async def create_task(   
    workspace_id: int,
    task_in: TaskCreate,
    token: str = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    return await task_crud.create_task(conn=conn, workspace_id=workspace_id, task=task_in)

# Get specific Task
@router.get("/{workspace_id}/{task_id}", response_model=TaskAllOut) 
async def get_task(workspace_id: int, 
                   task_id: int, 
                   token: str = Depends(get_current_user),
                   conn: asyncpg.Connection = Depends(get_db_connection)):
    task = await task_crud.get_task(conn=conn, workspace_id=workspace_id, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task or workspace not found")
    return task

# Get all Tasks in a Workspace
@router.get("/{workspace_id}", response_model=List[TaskAllOut]) 
async def get_all_tasks(workspace_id: int, 
                        token: str = Depends(get_current_user),
                        conn: asyncpg.Connection = Depends(get_db_connection)):

    get = await task_crud.get_tasks_by_workspace(conn=conn, workspace_id=workspace_id)
    if not get:
        raise HTTPException(status_code=404, detail="Workspace does not exist")
    return get

# Update a task
@router.patch("/{workspace_id}/{task_id}")
async def patch_task(
    workspace_id: int,
    task_id: int,
    patch_task: TaskPatch,
    token: str = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    task = await task_crud.patch_task(
        conn=conn,
        workspace_id=workspace_id,
        task_id=task_id,
        patch_task=patch_task   
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Delete Task
@router.delete("/{workspace_id}/{task_id}")
async def delete_task(workspace_id: int, 
                      task_id: int, 
                      token: str = Depends(get_current_user),
                      conn: asyncpg.Connection = Depends(get_db_connection)):
    deleted = await task_crud.delete_task(conn=conn, workspace_id=workspace_id, task_id=task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "success", "message": "Task deleted"}
