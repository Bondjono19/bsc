import os

LEN = os.getenv("EMBEDDING_VECTOR_LEN")

def parseEmbedding(embedding: list[float]):
    if not len(embedding) == LEN:
        return False
    