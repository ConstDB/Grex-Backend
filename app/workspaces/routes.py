from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import date
from ..deps import get_db_connection
import asyncpg
from ..workspaces.schemas import WorkspaceCreation
from .crud import add_workspace_to_db


router = APIRouter()
    
@router.get("/testing")
async def Testing():
    return "hello this is workspaces route"

@router.post("/workspace")
async def create_workspace(workspace: WorkspaceCreation, conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        workspace_dict = workspace.model_dump()
        
        res = await add_workspace_to_db(workspace_dict, conn)
        return res
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Workspace creation failed -> {e}")
     
@router.get("/workspace/{user_id}")
async def get_all_workspaces(conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        return{"message": "success", "data": conn}
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")

@router.get("/workspace/{user_id}/{workspace_id}")
async def get_workspace_info(conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        return{"message": "info fetched","data":conn}
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Process Failed -> {e}")
"""
@router.get("/users")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.add_user_to_db(user, db)

@router.get("/users/{user_id:}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user(db, user_id)    
"""
   