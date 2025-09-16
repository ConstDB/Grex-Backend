from .utils.embedding import compute_embedding
from .utils.query_classifier import query_classifier
from .vectorstore.message_vector_store import ProcessMessageLogs
from app.utils.logger import logger
from .crud import fetch_related_messages_db, fetch_previous_messages_db
from .gemini.prompts import generate_choice_1_content
from .gemini.client import gemini_setup
import asyncio
import asyncpg
import numpy as np

process = ProcessMessageLogs()

async def handle_query_service(payload: dict, conn: asyncpg.Connection):
    
    query= f"({payload["role"]} {payload["nickname"]} : {payload["query"]})"
    workspace_id=payload["workspace_id"]

    embedding = compute_embedding(query)
    choice = query_classifier(payload["query"])

    if choice == 0:
        res = await prepare_context_messages(embedding, workspace_id, query, conn)
    elif choice == 1:
        pass
    elif choice == 2:
        pass
    elif choice == 3:
        pass
    
    return res

async def prepare_context_messages(embedding: np.ndarray, workspace_id:int, query: str, conn: asyncpg.Connection):
    related_ids = await process.get_message_embeddings(embedding, workspace_id)
    
    message_ids=[]

    for id in related_ids:
        message_ids.append(id.payload["message_id"])

    related_records = await fetch_related_messages_db(message_ids, conn)
    previous_records = await fetch_previous_messages_db(workspace_id, conn)

    related_messages = await format_fetched_messages(related_records)
    previous_messages = await format_fetched_messages(previous_records)

    prompt = generate_choice_1_content(previous_messages, related_messages, query)

    return gemini_setup(prompt)

async def format_fetched_messages(messages: asyncpg.Record):
    count = 1
    result = """"""
    for message in messages:
        result += f"{count}. ({message["role"]}) {message["nickname"]} : {message["content"]} "
        count+=1
    return result