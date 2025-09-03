from .utils.embedding import compute_embedding
from qdrant_client.models import PointStruct
from ..utils.logger import logger
from .qdrant_config import qdrant, TASKS_COLLECTION_NAME
import asyncio
