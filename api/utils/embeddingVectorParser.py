def parseEmbedding(embeddings: list[list[float]]) -> bool:
    for embedding in embeddings:
        if not len(embedding) == 512:
            return False
    return True
    