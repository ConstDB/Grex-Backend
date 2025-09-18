from fastapi import Depends, HTTPException
import asyncpg
from asyncpg.exceptions import UniqueViolationError
from ..utils.query_builder import insert_query, get_query, update_query
from ..utils.logger import logger
from datetime import datetime, timezone
from .schemas import GetFiles

async def insert_messages_to_db(message_data: dict, conn:asyncpg.Connection):
    try:
        query = insert_query(message_data, table="messages", returning="message_id")
        
        res = await conn.fetchval(query, *message_data.values())

        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert message into Messages table -> {e}")

async def insert_text_messages_to_db(text_data: dict, conn: asyncpg.Connection):
    try:
        query = insert_query(text_data, table="text_messages")

        await conn.fetchrow(query, *text_data.values())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert text_message into text_messages table -> {e}")

async def get_few_messages_from_db(workspace_id: int, conn: asyncpg.Connection, last_id:int = None):
    try:
        if last_id:
            query = """
                SELECT *
                FROM message_details
                WHERE workspace_id = $1 
                    AND message_id < $2
                ORDER BY message_id DESC
                LIMIT $3
            """
            res = await conn.fetch(query, workspace_id, last_id, 30)
        else:
            query ="""
                SELECT *
                FROM message_details
                WHERE workspace_id = $1
                ORDER BY message_id DESC
                LIMIT $2
            
            """
            res = await conn.fetch(query, workspace_id, 30)
            
        res.reverse()
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages from DB -> {e}")

async def update_last_read_timestamp(workspace_id: int, user_id: int, conn: asyncpg.Connection):
    try:
        payload = {"last_read_at": datetime.now(timezone.utc)}
        query = update_query("workspace_id", "user_id", model=payload, table="message_read_status")

        return await conn.execute(query, *payload.values(), workspace_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update timestamp -> {e}")

async def get_last_read_timestamp(workspace_id: int, user_id: int, conn: asyncpg.Connection):
    try:
        query = get_query("workspace_id", "user_id", fetch="last_read_at", table="message_read_status")
        return await conn.fetchrow(query, workspace_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user's last_read_at timestamp -> {e}")


async def get_sender_data(user_id: int, workspace_id: int, conn: asyncpg.Connection):
    query = """
        SELECT
            u.profile_picture,
            wm.nickname
        FROM users u
        LEFT JOIN workspace_members wm ON u.user_id = wm.user_id
        WHERE u.user_id = $1
            AND wm.workspace_id = $2
    """

    res = await conn.fetchrow(query, user_id, workspace_id)

    return res

async def fetch_attachments_db(
    workspace_id: int, 
    file_type: str, 
    conn: asyncpg.Connection):
    
    query = """
        SELECT
            ma.attachment_id,
            ma.message_id,
            ma.file_name as name,
            ma.file_type as type,
            ma.file_url as url,
            ma.file_size as size,
            ma.uploaded_at
        FROM message_attachments ma
        JOIN messages m ON ma.message_id = m.message_id
        WHERE m.workspace_id = $1
        AND ma.file_type = $2
        ORDER BY ma.uploaded_at DESC;

    """
    res = await conn.fetch(query, workspace_id, file_type)
    return [dict(row) for row in res]


async def fetch_replied_message_db(message_id:int, workspace_id:int, conn: asyncpg.Connection):
    query = """
        SELECT
            m.message_id,
            wm.nickname as sender_name,
            COALESCE(
                tm.content,
                ma.file_url
            ) AS content
        FROM messages m
        LEFT JOIN text_messages tm ON m.message_id = tm.message_id
        LEFT JOIN message_attachments ma ON m.message_id = ma.message_id
        LEFT JOIN workspace_members wm ON wm.user_id = m.sender_id AND wm.workspace_id = $2
        WHERE m.message_id = $1 AND m.workspace_id = $2
    """

    res = await conn.fetchrow(query, message_id, workspace_id)

    return res