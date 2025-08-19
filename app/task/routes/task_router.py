# app/api/routes/task.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List
import asyncpg
from app.db.connection import get_connection  
from app.task.schemas.Tasks_schema import taskCreate, TaskOut, taskUpdate
from app.task.crud import task_crud

router = APIRouter(prefix="/task", tags=["task"])

@router.post("/{workspace_id}") # Create Task
async def create_task(workspace_id: int, task_in: taskCreate, conn: asyncpg.Connection = Depends(get_connection)):
    return await task_crud.create(conn=conn, workspace_id=workspace_id, obj_in=task_in)

@router.get("/{workspace_id}/{task_id}", response_model=TaskOut) # Get specific Task
async def get_task(workspace_id: int, task_id: int, conn: asyncpg.Connection = Depends(get_connection)):
    task = await task_crud.get(conn=conn, workspace_id=workspace_id, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/{workspace_id}", response_model=List[TaskOut]) # Get all Tasks in a Workspace
async def get_all_tasks(workspace_id: int, conn: asyncpg.Connection = Depends(get_connection)):
    return await task_crud.get_all(conn=conn, workspace_id=workspace_id)

@router.put("/{workspace_id}/{task_id}", response_model=TaskOut)# Update Task
async def update_task(workspace_id: int, task_id: int, task_in: taskUpdate, conn: asyncpg.Connection = Depends(get_connection)):
    task = await task_crud.update(conn=conn, workspace_id=workspace_id, task_id=task_id, obj_in=task_in)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{workspace_id}/{task_id}") # Delete Task
async def delete_task(workspace_id: int, task_id: int, conn: asyncpg.Connection = Depends(get_connection)):
    deleted = await task_crud.delete(conn=conn, workspace_id=workspace_id, task_id=task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "success", "message": "Task deleted"}
