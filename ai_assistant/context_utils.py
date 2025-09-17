from .crud import fetch_related_messages_db, fetch_previous_messages_db
from .vectorstore.message_vector_store import ProcessMessageLogs
import asyncpg
import numpy as np
process = ProcessMessageLogs()


async def prepare_context_messages(embedding: np.ndarray, workspace_id:int, query: str, conn: asyncpg.Connection):
    related_ids = await process.get_message_embeddings(embedding, workspace_id)
    
    message_ids=[]

    for id in related_ids:
        message_ids.append(id.payload["message_id"])

    related_records = await fetch_related_messages_db(message_ids, conn)
    previous_records = await fetch_previous_messages_db(workspace_id, conn)

    related_messages = await format_fetched_messages(related_records)
    previous_messages = await format_fetched_messages(previous_records)

    return related_messages, previous_messages

async def format_fetched_messages(messages: asyncpg.Record):
    count = 1
    result = """"""
    for message in messages:
        result += f"{count}. ({message["role"]}) {message["nickname"]} : {message["content"]} "
        count+=1
    return result


