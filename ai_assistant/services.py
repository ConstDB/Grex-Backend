from .utils.embedding import compute_embedding
from .utils.query_classifier import query_classifier
from .vectorstore.message_vector_store import ProcessMessageLogs
import numpy as np

process = ProcessMessageLogs()

async def handle_query_service(query:str):
    embedding = compute_embedding(query)
    choice = query_classifier(query)

    if choice == 0:
        pass
    elif choice == 1:
        pass
    elif choice == 2:
        pass
    elif choice == 3:
        pass
    
async def prepare_context_messages(embedding: np.ndarray):
    process.get_message_embeddings()
