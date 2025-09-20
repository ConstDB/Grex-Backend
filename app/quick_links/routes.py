import asyncpg
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import date
from ..deps import get_db_connection
from .crud import fetch_workspace_link_db, remove_workspace_link_db, create_workspace_links_db,update_link_db
from ..users.auth import get_current_user
from .schemas import GetLinks,CreateLinks,PutLink



router = APIRouter()

@router.put("/workspace/{workspace_id}/quick-links")
async def update_workspace_link_route(
    workspace_id:int,
    link_id:int,
    UpdateLink: PutLink,
    conn:asyncpg.Connection=Depends(get_db_connection),
    token:str=Depends(get_current_user)
):
    try:
         
        res = await update_link_db(workspace_id, link_id, UpdateLink, conn)
        return res
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"process failed -> {e}")


@router.post("/workspace/{workspace_id}/quick-links",response_model=GetLinks)
async def add_workspace_links_route(
    workspace_id:int, 
    link:CreateLinks,
    conn:asyncpg.Connection = Depends(get_db_connection),
    token:str = Depends(get_current_user)
):
    try:
        
        
        res = await create_workspace_links_db(workspace_id, link, conn)
        return res
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"process failed -> {e}")
    

@router.get("/workspace/{workspace_id}/links/quick", response_model=List[GetLinks])
async def get_workspace_links_route(
workspace_id: int,                              
conn:asyncpg.Connection=Depends(get_db_connection),
    token: str = Depends(get_current_user)):  
    try:
        
        res = await fetch_workspace_link_db(workspace_id, conn)
        return res 
    except Exception as e:
        raise HTTPException(status_code = 500, detail =f"process ay mali -> {e}")
    
        
@router.delete("/workspace/{workspace_id}/links/quick")
async def delete_workspace_link_route(
    link_id:int, conn:asyncpg.Connection = Depends(get_db_connection),
    token:str = Depends(get_current_user)):
    try:
        
        res = await remove_workspace_link_db(link_id, conn)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"process failed -> {e}")
    
        




