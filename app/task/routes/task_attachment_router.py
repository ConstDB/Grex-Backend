# app/api/task/routes/task_attachment_router.py

from fastapi import APIRouter, Depends, HTTPException
from ...deps import get_db_connection  
from ...authentication.services import get_current_user
from ...task.schemas.TaskAttachment_schema import TaskAttachmentCreate, TaskAttachmentDelete
from ...task.crud.task_attachment_crud import create_attachment, get_attachments_by_task, delete_attachment

router = APIRouter()

# Create a task attachment
@router.post("/task/{task_id}/attachments")
async def add_attachment(task_id: int, 
                         attachment: TaskAttachmentCreate,
                         token: str = Depends(get_current_user), 
                         conn=Depends(get_db_connection)):
    try:
        row = await create_attachment(conn, task_id, attachment)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return row

# Get task attachment
@router.get("/task/{task_id}/attachments")
async def fetch_attachments(task_id: int, 
                            token: str = Depends(get_current_user),
                            conn=Depends(get_db_connection)):
    
    rows = await get_attachments_by_task(conn, task_id)
    return rows

# Delete a task attachment
@router.delete("/task/{task_id}/attachments")
async def remove_attachment(attachment: TaskAttachmentDelete, 
                            token: str = Depends(get_current_user),
                            conn=Depends(get_db_connection)):
    
    row = await delete_attachment(conn, attachment)
    if not row:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return{"status": "success", "message": "Task attachment removed"} 
