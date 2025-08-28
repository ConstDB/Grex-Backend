from fastapi import Depends, HTTPException
import asyncpg
from asyncpg.exceptions import UniqueViolationError
from ..utils.query_builder import insert_query, get_query, update_query
from ..utils.logger import logger
from datetime import datetime, timezone

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

async def get_few_messages_from_db(workspace_id: int, timestamp: datetime, conn: asyncpg.Connection):
    try:
        query ="""
            SELECT *
            FROM message_details
            WHERE workspace_id = $1 
            AND sent_at < $2
            ORDER BY sent_at DESC
            LIMIT $3
        """

        res = await conn.fetch(query, workspace_id, timestamp, 30)

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