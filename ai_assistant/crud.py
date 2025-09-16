from app.utils.query_builder import get_query
import asyncpg
from fastapi import HTTPException

async def fetch_related_messages_db(message_id: list, conn: asyncpg.Connection):
    query = """
        SELECT tm.content, wm.nickname, wm.role FROM messages m
        LEFT JOIN text_messages tm ON m.message_id = tm.message_id
        LEFT JOIN workspace_members wm ON m.sender_id = wm.user_id AND m.workspace_id = wm.workspace_id
        WHERE m.message_id = ANY($1::int[])
    """
    return await conn.fetch(query, message_id)

async def fetch_previous_messages_db(workspace_id: int, conn: asyncpg.Connection, limit:int = 10):
    query="""
        SELECT tm.content, wm.nickname, wm.role FROM messages m
        LEFT JOIN text_messages tm ON m.message_id = tm.message_id
        LEFT JOIN workspace_members wm ON m.sender_id = wm.user_id AND m.workspace_id = wm.workspace_id
        WHERE m.workspace_id = $1
        ORDER BY m.message_id DESC
        LIMIT $2
    """

    res = await conn.fetch(query, workspace_id, limit)

    res.reverse()
    return res
    
    