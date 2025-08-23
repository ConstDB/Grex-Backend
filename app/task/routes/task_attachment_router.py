# app/api/task/routes/task_attachment_router.py

from fastapi import APIRouter, Depends, HTTPException
from ...deps import get_db_connection  
from app.task.schemas.TaskAttachment_schema import TaskAttachmentCreate, TaskAttachmentDelete
from app.task.crud.task_attachment_crud import create_attachment, get_attachments_by_task, delete_attachment

router = APIRouter()

# Create a task attachment
@router.post("/")
async def add_attachment(attachment: TaskAttachmentCreate, conn=Depends(get_db_connection)):
    try:
        row = await create_attachment(conn, attachment)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return row

# Get task attachment
@router.get("/{task_id}")
async def fetch_attachments(task_id: int, conn=Depends(get_db_connection)):
    rows = await get_attachments_by_task(conn, task_id)
    return rows

# Delete a task attachment
@router.delete("/")
async def remove_attachment(attachment: TaskAttachmentDelete, conn=Depends(get_db_connection)):
    row = await delete_attachment(conn, attachment)
    if not row:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return{"status": "success", "message": "Task attachment removed"} 
