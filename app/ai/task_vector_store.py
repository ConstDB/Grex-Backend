from .utils.embedding import compute_embedding
from qdrant_client.models import PointStruct
from ..utils.logger import logger
from .qdrant_config import qdrant, TASKS_COLLECTION_NAME
import asyncio
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
            print(res)
        except Exception as e:
            # logger.info(f"Failed to insert user to Qdrant -> {e}")
            print(f"Failed to insert user to Qdrant -> {e}")


    # asyncio.run(insert_task_logs_to_vdb(1,1, task_logs))


    async def get_task_embeddings(self):
        try:
            records, _ = await qdrant.scroll(
                collection_name=self.task,
                limit=10,
                with_payload=True,
                with_vectors=True
            )
            for r in records:
                print(f"id : {r.id}")
                print(f"vector : {r.vector}")
                print(f"payload : {r.payload}")
        except Exception as e:
            print(f"Failed to fetch task logs embeddings -> {e}")

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

