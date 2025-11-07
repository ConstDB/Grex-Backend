from ..utils.embedding import compute_embedding
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
from app.utils.logger import logger
from .qdrant_config import qdrant, TASKS_COLLECTION_NAME
import asyncio
import numpy as np
from collections import deque



class ProcessTaskLog:

    def __init__(self):
        self.task = TASKS_COLLECTION_NAME
        self.task_logs_queue= deque()


    async def insert_task_logs_to_vdb(self, task_log_id:int, workspace_id:int, content:str):
        try:
            embedding = compute_embedding(content)
            point = PointStruct(id=task_log_id, vector=embedding, payload={"task_log_id": task_log_id, "workspace_id": workspace_id})
            res = await qdrant.upsert(collection_name=self.task, points=[point]) 
        except Exception as e:
            logger.error(f"Failed to insert user to Qdrant -> {e}")

    async def get_task_embeddings(self, embedding: np.ndarray, workspace_id: int):
        try:
            cluster_filter = FieldCondition(
                key="workspace_id",
                match=MatchValue(value=workspace_id)
            )

            search_filter = Filter(must=cluster_filter)

            records = await qdrant.search(
                collection_name=self.task,
                query_vector=embedding,
                limit=10,
                with_payload=True,
                with_vectors=False,
                query_filter=search_filter
            )

            return records
        except Exception as e:
            logger.error(f"Failed to fetch task logs embeddings -> {e}")

    async def insert_data(self,task_log_id:int, workspace_id:int, content:str ):
        data = {
            "task_log_id": task_log_id, "workspace_id": workspace_id, "content": content
        }
        
        self.task_logs_queue.append(data)

        if len(self.task_logs_queue) == 1:
            asyncio.create_task(self.queue())

    async def queue(self):

        while self.task_logs_queue:
            try:
                log = self.task_logs_queue.popleft()
                await self.insert_task_logs_to_vdb(log["task_log_id"], log["workspace_id"], log["content"])
            except Exception as e:
                logger.error(f"Failed to insert task log:{log["task_log_id"]} to qdrant : {e}")
        logger.info("Task queue is empty.")

