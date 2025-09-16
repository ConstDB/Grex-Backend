from fastapi import APIRouter, Depends, HTTPException
from ..deps import get_db_connection
from ..users.auth import get_current_user
from ..categories.crud import insert_category_db, update_category_db, fetch_category_db, delete_category_db
from ..categories.schema import CategoryCreate, CategoryUpdate, CategoryOut, CategoryDelete
import asyncpg


router = APIRouter()

# For posting a category in workspaces
@router.post("/workspace/{workspace_id}/categories", response_model=CategoryOut)
async def post_category_route(
    workspace_id: int, 
    category: CategoryCreate,
    token: str = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    try:
        row = await insert_category_db(conn, workspace_id, category)
        return row
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# For getting a category in workspaces
@router.get("/workspace/{workspace_id}/categories", response_model=list[CategoryOut])
async def get_category_route(
    workspace_id: int,
    token: str = Depends(get_current_user), 
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    rows = await fetch_category_db(conn, workspace_id)
    return rows


# For updating a category in workspaces
@router.put("/workspace/{workspace_id}/categories/{category_id}", response_model=CategoryOut)
async def put_category_route(workspace_id: int,
                       category_id: int,
                       category: CategoryUpdate,
                       token: str = Depends(get_current_user),
                       conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        row = await update_category_db(conn, workspace_id, category_id, category)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return row

# For deleting category
@router.delete("/workspace/{workspace_id}/categories/{category_id}", response_model=CategoryDelete)
async def delete_category_route(workspace_id: int,
                       category_id: int,
                       token: str = Depends(get_current_user),
                       conn: asyncpg.Connection = Depends(get_db_connection)):
    row = await delete_category_db(conn, workspace_id, category_id)
    if not row:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"status": "success", "message": "Category Deleted"}

