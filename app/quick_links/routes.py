import asyncpg
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import date
from ..deps import get_db_connection
from .crud import fetch_workspace_link_db
from ..users.auth import get_current_user
from .schemas import GetLinks



router = APIRouter()

"""@router.post("/workspace/{workspace_id}/quick-links")
async def add_workspace_links_route(
    workspace_id:int, 
    conn:asyncpg.Connection = Depends(get_db_connection)
):
    try:"""

@router.get("/workspace/{workspace_id}/links/quick", response_model=List[GetLinks])
async def get_workspace_links_route(workspace_id: int, 
conn:asyncpg.Connection=Depends(get_db_connection),
    token: str = Depends(get_current_user)):  
    try:
        
        
        res = await fetch_workspace_link_db(workspace_id, conn)
        return res 
    except Exception as e:
        raise HTTPException(status_code = 500, detail =f"process ay mali{e}")
        
        




