from .utils.embedding import compute_embedding
from qdrant_client.models import PointStruct
from ..utils.logger import logger
from .qdrant_config import qdrant, MESSAGES_COLLECTION_NAME
import asyncio

message_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit"


class ProcessMessageLogs:

    def __init__(self):
        self.message = MESSAGES_COLLECTION_NAME

    async def insert_message_to_vdb(self, workspace_id:int, message_id: int, content: str):
        try:
            embedding = compute_embedding(content)
            point = PointStruct(id=message_id, vector=embedding, payload={"message_id" : message_id, "workspace_id":workspace_id})
            res = await qdrant.upsert(collection_name=self.message, points=[point])
            
        except Exception as e:
            print(f"failed to insert message into qdrant -> {e}")


    # asyncio.run(insert_message_to_vdb(1, 1, message_text))

    async def get_message_embeddings(self):
        try:
            records, _ = await qdrant.scroll(
                collection_name=self.message,
                limit=10,
                with_payload=True,
                with_vectors=True
            )
            for r in records:
                print(f"id : {r.id}")
                print(f"vector : {r.vector}")
                print(f"payload : {r.payload}")
        except Exception as e:
            print(f"Failed to fetch message logs embeddings -> {e}")


asyncio.run(get_message_embeddings())