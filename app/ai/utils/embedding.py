from sentence_transformers import SentenceTransformer
from ...utils.logger import logger
import numpy as np
import transformers


transformer = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
tokenizer = transformers.AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")



# s = """Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.
#      It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for 'lorem ipsum' will uncover many web sites still in their infancy. Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like).

# """


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
