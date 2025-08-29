from fastapi import APIRouter, Depends, HTTPException
from ..deps import get_db_connection
from ..users.auth import get_current_user
from ..categories.crud import create_category, update_category, get_category, delete_category
from ..categories.schema import CategoryCreate, CategoryUpdate, CategoryOut
import asyncpg
from typing import List

router = APIRouter()

@router.post("/workspace/{workspace_id}/categories", response_model=CategoryOut)
async def post_category(workspace_id: int, 
                        category: CategoryCreate,
                        token: str = Depends(get_current_user),
                        conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        row = await create_category(conn, workspace_id, category)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return row

@router.get("/workspace/{workspace_id}/categories", response_model=List[CategoryOut])
async def get_categories(workspace_id: int, 
                         token: str = Depends(get_current_user),
                         conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        rows = await get_category(conn, workspace_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return rows

@router.put("/workspace/{workspace_id}/category/{category_id}", response_model=CategoryOut)
async def put_category(workspace_id: int,
                       category_id: int,
                       category: CategoryUpdate,
                       token: str = Depends(get_current_user),
                       conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        row = await update_category(conn, workspace_id, category_id, category)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return row

@router.delete("/workspace/{workspace_id}/category/{category_id}", response_model=CategoryOut)
async def del_category(workspace_id: int,
                       category_id: int,
                       token: str = Depends(get_current_user),
                       conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        row = await delete_category(conn, workspace_id, category_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return row
