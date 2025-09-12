from sentence_transformers import SentenceTransformer
from ...utils.logger import logger
import numpy as np
import transformers


transformer = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
tokenizer = transformers.AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

def compute_embedding(text):
    """
        Transform text into embeddings
    """
    try:
        chunks = chunk_text(text) # chunk text

        embeddings = transformer.encode(chunks) # convert text into embeddings

        #  return the average embeddings
        return np.mean(embeddings, axis=0)
    except Exception as e:
        logger.info(f"Failed to compute embeddings -> {e}")

def chunk_text(text:str, max_tokens: int = 200, token_overlap:int = 20):
    try: 
        # tokenize text
        tokens = tokenizer.encode(text, add_special_tokens=False)

        chunks = []

        for i in range(0, len(tokens), max_tokens - token_overlap):
            # to avoid irelevance of each chunks, there will be overlap in each chunks
            chunk = tokens[i:i+max_tokens]

            if not chunk:
                break
            
            chunks.append(tokenizer.decode(chunk))
        return chunks

    except Exception as e:
        logger.info(f"Failed to chunk_text -> {e}")
        # print(f"Failed to chunk_text -> {e}")

def queue_function():
    pass