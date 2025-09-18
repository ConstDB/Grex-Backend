from fastapi import APIRouter, Depends, HTTPException
from ...deps import get_db_connection
from ...users.auth import get_current_user
from ...task.crud import task_assignment_crud
from ...task.schemas.TaskAssignment_schema import TaskAssignmentOut
from typing import List
import asyncpg

router = APIRouter()

# Router for assigning users onto task
@router.post("/task/{task_id}/assignment/{user_id}")
async def create_taskassignment(
    task_id: int, 
    user_id: int, 
    token: str = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_connection)):
    assigned = await task_assignment_crud.create_taskassignment(conn, task_id, user_id)
    return {
        "status": "success",
        "message": f"User {user_id} was assigned to Task {task_id}",
        "data": assigned
    }

# Router for getting all assigned users from a task
@router.get("/task/{task_id}/assignment", response_model=List[TaskAssignmentOut])
async def get_taskassignment(task_id: int, 
                             token: str = Depends(get_current_user),
                             conn: asyncpg.Connection = Depends(get_db_connection)):
    taskassignment = await task_assignment_crud.get_taskassignment(conn, task_id)
    return [TaskAssignmentOut(**r) for r in taskassignment] if taskassignment else []

# Router for removing assigned users from task
@router.delete("/task/{task_id}/assignment/{user_id}")
async def delete_taskassignment(task_id: int, 
                                user_id: int, 
                                token: str = Depends(get_current_user),
                                conn: asyncpg.Connection = Depends (get_db_connection)):
    remove = await task_assignment_crud.delete_taskassignment(conn, task_id, user_id)
    if not remove:
        raise HTTPException(status_code=400, detail="Failed to remove user")
    return{"status": "success", "message": "User removed from assigned task"}