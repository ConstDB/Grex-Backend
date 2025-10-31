from fastapi import APIRouter, Depends, HTTPException
from ...deps import get_db_connection
from ...authentication.services import get_current_user
from typing import List
from ...task.crud import task_comment_crud
from ...task.schemas.TaskComment_schema import TaskCommentCreate, TaskCommentUpdate, TaskCommentOut, CreateCommentOut
import asyncpg

router = APIRouter()

# Router for posting comments in task
@router.post("/task/{task_id}/comments")
async def create_taskcomment(task_id: int, 
                             taskcomment: TaskCommentCreate, 
                             token: str = Depends(get_current_user),
                             conn: asyncpg.Connection = Depends(get_db_connection)):
    row = await task_comment_crud.create_taskcomment(conn, task_id, taskcomment)
    if not row:
        raise HTTPException(status_code=400, detail="Failed to comment on task")
    return  CreateCommentOut(**row)

# Router for getting comments in a task
@router.get("/task/{task_id}/comments/", response_model=List[TaskCommentOut])
async def get_taskcomment(task_id: int,
                          token: str = Depends(get_current_user),
                          conn: asyncpg.Connection = Depends(get_db_connection)):  
    rows = await task_comment_crud.get_taskcomment(conn, task_id)
    return [TaskCommentOut(**r) for r in rows] if rows else []

# Router for updating comment contents
@router.put("/task/{task_id}/comments/{comment_id}")
async def update_taskcomment(task_id: int,
                            comment_id: int,
                            update_taskcomment: TaskCommentUpdate,
                            token: str = Depends(get_current_user), 
                            conn: asyncpg.Connection = Depends(get_db_connection)):
    put = await task_comment_crud.update_taskcomment(conn, task_id, comment_id, update_taskcomment)
    if not put:
        raise HTTPException(status_code=404, detail="Comment not found invalid task_id")
    return put

 # Router for removing comments
@router.delete("/task/{task_id}/comments/{comment_id}")
async def delete_taskcomment(task_id: int, 
                             comment_id: int, 
                             token: str = Depends(get_current_user),
                             conn: asyncpg.Connection = Depends(get_db_connection)):
    
    query = "DELETE FROM task_comments WHERE comment_id = $1 AND task_id = $2 RETURNING *;"
    row = await conn.fetchrow(query, comment_id, task_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Comment {comment_id} in task {task_id} not found")
    return {"status": "success","message": f"Comment {comment_id} removed successfully from task {task_id}","deleted_comment": dict(row)}
