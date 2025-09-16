from fastapi import APIRouter, Depends
from app.deps import get_db_connection
from app.users.auth import get_current_user
from .services import handle_query_service
from .schemas import QueryPayload
import asyncpg

router = APIRouter()

@router.post("/assistant/query")
async def handle_query_route(payload:QueryPayload, conn: asyncpg.Connection = Depends(get_db_connection)):
    return await handle_query_service(payload.model_dump(), conn)