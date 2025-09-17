from .crud import fetch_related_messages_db, fetch_previous_messages_db, fetch_related_task_logs_db, fetch_recent_tasks_db
from .vectorstore.message_vector_store import ProcessMessageLogs
from .vectorstore.task_vector_store import ProcessTaskLog
from app.utils.logger import logger
import asyncpg
import numpy as np
message_process = ProcessMessageLogs()
task_process = ProcessTaskLog()

async def prepare_context_messages(embedding: np.ndarray, workspace_id:int, query: str, conn: asyncpg.Connection):
    related_ids = await message_process.get_message_embeddings(embedding, workspace_id)
    
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

async def format_fetched_tasks(logs: asyncpg.Record):
    count = 1
    result = """"""
    for log in logs:
        result += f"{count}. {log["context"]}    "
        count += 1

    return result

async def format_recent_tasks(tasks: asyncpg.Record):
    count = 1
    result = """"""

    for task in tasks:
        result += f"{count}. Task '{task["title"]}'({task["task_id"]}) with a description of ({task["description"]}). Its duration is from {task["start_date"]} to {task["deadline"]}. the one who created this task is {task["first_name"]}, and right now it is {task["status"]}, it was assigned to: {task["assignees"]}"

    return result

async def prepare_tasks_context(embedding: np.ndarray, workspace_id:int, query:str, conn: asyncpg.Connection):
    related_ids = await task_process.get_task_embeddings(embedding, workspace_id)

    task_ids = []
    for id in related_ids:
        task_ids.append(id.payload["task_log_id"])

    related_records = await fetch_related_task_logs_db(task_ids, conn)
    related_logs = await format_fetched_tasks(related_records)

    recent_records = await fetch_recent_tasks_db(workspace_id, conn)
    recent_tasks = await format_recent_tasks(recent_records)

    # logger.info(recent_tasks)
    return related_logs, recent_tasks