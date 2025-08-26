from fastapi import APIRouter, Depends, HTTPException
from ...deps import get_db_connection
from app.task.crud import task_assignment_crud
import asyncpg

router = APIRouter()

# Router for assigning users onto task
@router.post("/task/{task_id}/assignment/{user_id}")
async def create_taskassignment(
    task_id: int, 
    user_id: int, 
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    assigned = await task_assignment_crud.create_taskassignment(conn, task_id, user_id)
    if not assigned:
        raise HTTPException(status_code=400, detail="Failed to assign user to task")

    return {
        "status": "success",
        "message": f"User {user_id} was assigned to Task {task_id}",
        "data": assigned
    }

# Router for getting all assigned users from a task
@router.get("/task/{task_id}/assignment")
async def get_taskassignment(task_id: int, conn: asyncpg.Connection = Depends(get_db_connection)):
    taskassignment =  await task_assignment_crud.get_taskassignment(conn, task_id)
    if not taskassignment:
        raise HTTPException(status_code=400, detail="No assigned users")
    return{"status": "success", 
           "message": f"Assigned users in task {task_id}", 
           "data": taskassignment
           }

# Router for removing assigned users from task
@router.delete("/task/{task_id}/assignment/{user_id}")
async def delete_taskassignment(task_id: int, user_id: int, conn: asyncpg.Connection = Depends (get_db_connection)):
    remove = await task_assignment_crud.delete_taskassignment(conn, task_id, user_id)
    if not remove:
        raise HTTPException(status_code=400, detail="Failed to remove user")
    return{"status": "success", "message": "User removed from assigned task"}