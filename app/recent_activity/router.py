from fastapi import APIRouter, Depends
from ..deps import get_db_connection
from ..authentication.services import get_current_user
from .schema import RecentActivityOut
from .crud import get_activity_db
from typing import List
import asyncpg

router = APIRouter()

@router.get("/workspaces/{workspace_id}/recent-activities", response_model=List[RecentActivityOut])
async def fetch_activity_route(
    workspace_id: int,
    token: str = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    return await get_activity_db(conn, workspace_id)