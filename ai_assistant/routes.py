from fastapi import APIRouter, Depends
from app.deps import get_db_connection
from app.users.auth import get_current_user

router = APIRouter()

@router.get("/assistant/query")
async def handle_query_route(query:str):
    pass