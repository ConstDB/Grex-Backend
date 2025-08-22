from fastapi import Depends, HTTPException
import asyncpg
from asyncpg.exceptions import UniqueViolationError
from ..utils.query_builder import insert_query, get_query, update_query
from ..utils.logger import logger

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