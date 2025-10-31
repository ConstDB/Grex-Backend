from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType
from app.utils.logger import logger
from ...app.config.settings import settings as st

qdrant = AsyncQdrantClient(url=st.QDRANT_URL, api_key=st.QDRANT_API_KEY)

TASKS_COLLECTION_NAME = "task_logs"
MESSAGES_COLLECTION_NAME = "messages_logs"
EMBEDDING_DIM = 384

async def ensure_collection(client: AsyncQdrantClient, name:str, dim:int, id: int):
    """ checks if collection exists"""
    exists = await client.collection_exists(name)

    if not exists:
        await client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
        )
        await client.create_payload_index(
            collection_name=name,
            field_name=id,
            field_schema=PayloadSchemaType.INTEGER
        )
        await client.create_payload_index(
            collection_name=name,
            field_name="workspace_id",
            field_schema=PayloadSchemaType.INTEGER
        )
        logger.info(f"{name} collection created.")
    else:
        logger.info(f"Collection {name} already exists")

async def setup_collection():
    """ calls ensure_collection"""
    await ensure_collection(qdrant, TASKS_COLLECTION_NAME, EMBEDDING_DIM, "task_log_id")
    await ensure_collection(qdrant, MESSAGES_COLLECTION_NAME, EMBEDDING_DIM, "message_id")

