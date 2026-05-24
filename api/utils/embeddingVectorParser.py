def parseEmbedding(embeddings: list[list[float]]) -> bool:
    if not embeddings:
        return True
    for embedding in embeddings:
        if not len(embedding) == 512:
            return False
    return True
    