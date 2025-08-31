from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType
from ..utils.logger import logger

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

qdrant = QdrantClient(host=qdrant, port=6333)

TASKS_COLLECTION_NAME = "task_logs"
MESSAGES_COLLECTION_NAME = "messages_logs"
EMBEDDING_DIM = 384

tasks = await qdrant.collection_exists(TASKS_COLLECTION_NAME)
messages = await qdrant.collection_exists(MESSAGES_COLLECTION_NAME)


async def ensure_collection(client: QdrantClient, name:str, dim:int, id: int):
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

