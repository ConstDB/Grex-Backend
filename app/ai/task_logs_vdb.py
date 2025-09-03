from .utils.embedding import compute_embedding
from qdrant_client.models import PointStruct
from ..utils.logger import logger
from .qdrant_config import qdrant, TASKS_COLLECTION_NAME
import asyncio

task = TASKS_COLLECTION_NAME

task_logs = "Leader None patched task_id 1. Changes: title changed from 'example' to 'string'"


async def insert_task_logs_to_vdb(task_log_id:int, workspace_id:int, content:str):
    try:
        embedding = compute_embedding(content)
        point = PointStruct(id=task_log_id, vector=embedding, payload={"task_log_id": task_log_id, "workspace_id": workspace_id})
        res = await qdrant.upsert(collection_name=task, points=[point]) 
        print(res)
    except Exception as e:
        # logger.info(f"Failed to insert user to Qdrant -> {e}")
        print(f"Failed to insert user to Qdrant -> {e}")


asyncio.run(insert_task_logs_to_vdb(1,1, task_logs))
