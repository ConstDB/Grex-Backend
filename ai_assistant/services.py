from .utils.embedding import compute_embedding
from .utils.query_classifier import query_classifier
from .context_utils import prepare_context_messages
from app.utils.logger import logger
from .gemini.prompts import generate_choice_0_content
from .gemini.client import gemini_setup
from app.messages.websocket import manager
from app.messages.crud import insert_messages_to_db, insert_text_messages_to_db
from app.db_instance import db
from datetime import datetime, timezone
import asyncpg
import numpy as np


async def handle_query_service(payload: dict, conn: asyncpg.Connection):
    """
        Classify query on what subsequent action to do.
    """
    query= f"({payload["role"]} {payload["nickname"]} : {payload["query"]})"
    workspace_id=payload["workspace_id"]
    message_id = payload["message_id"]

    embedding = compute_embedding(query)
    choice = query_classifier(payload["query"])

    if choice == 0:
        res = await execute_context_response_0(embedding, workspace_id, query, message_id, conn)
    elif choice == 1:
        pass
    elif choice == 2:
        pass
    elif choice == 3:
        pass
    

async def execute_context_response_0(embedding: np.ndarray, workspace_id:int, query: str, message_id: int, conn: asyncpg.Connection):
    """
        Execute subsequent action for choice 0(fetch recent and related message for our reasoner to be context-aware)
    """

    related_messages, recent_messages = await prepare_context_messages(embedding, workspace_id, query, conn)
    prompt = generate_choice_0_content(recent_messages, related_messages, query)
    output =  gemini_setup(prompt)

    await broadcast_grex_output(workspace_id, message_id, output)

async def broadcast_grex_output(workspace_id: int, reply_to: int, output:str):
    """
        Broadcast the output on the specified workspace's websocket
    """
    GREX_ID = 9999
    sender_cache = {}

    message_data= {
        "workspace_id": workspace_id,
        "sender_id": GREX_ID,
        "message_type": "text",
        "reply_to": reply_to 
    }

    async with db.get_connection() as conn:
        async with conn.transaction():

            if await manager.not_in_collection(f"{workspace_id}-{GREX_ID}"):
                sender_payload = {"profile_picture": None, "nickname": "Grex AI"}
                sender_cache = await manager.store_cache(f"{workspace_id}-{GREX_ID}", sender_payload)
            else:
                sender_cache = await manager.get_user_cache(f"{workspace_id}-{GREX_ID}")

            message_id = await insert_messages_to_db(message_data, conn)
            
            await insert_text_messages_to_db(text_data={"message_id": message_id, "content":output}, conn=conn)

    message_obj = {
        "message_id": message_id,
        "workspace_id": workspace_id,
        "sender_id": GREX_ID,
        "avatar": sender_cache["avatar"],
        "nickname": sender_cache["nickname"],
        "type": "text",
        "content": output,
        "reply_to": reply_to,
        "sent_at": datetime.now(timezone.utc)
    }

    logger.info(f"Message: \n {message_obj}")

    await manager.broadcast(workspace_id, message_obj)
