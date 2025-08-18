# app/api/routes/task.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.task.schemas.Tasks_schema import TaskCreate, TaskRead, TaskUpdate
from app.task.crud.task_crud import task_crud

router = APIRouter(prefix="/task", tags=["task"])

@router.post("/", response_model=TaskRead) #Create method for task
async def create_task(task_in: TaskCreate, db: AsyncSession = Depends(get_db)):
    return await task_crud.create(db=db, obj_in=task_in)

@router.get("/{task_id}", response_model=TaskRead)# Get method for a specific task
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await task_crud.get(db=db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/", response_model=List[TaskRead]) # Get method for task in a specific workspace
async def get_all_tasks(db: AsyncSession = Depends(get_db)):
    return await task_crud.get_all(db=db)

@router.put("/{task_id}", response_model=TaskRead) # Update method for task
async def update_task(task_id: int, task_in: TaskUpdate, db: AsyncSession = Depends(get_db)):
    task = await task_crud.update(db=db, id=task_id, obj_in=task_in)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}") # Delete method for task
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await task_crud.delete(db=db, id=task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "success", "message": "Task deleted"}
