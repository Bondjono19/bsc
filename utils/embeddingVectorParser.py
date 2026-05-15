import os

LEN = os.getenv("EMBEDDING_VECTOR_LEN")

def parseEmbedding(embedding: list[float]):
    print(len(embedding))
    if not len(embedding) == 512:
        return False
    return True
    