from api.utils.embeddingVectorParser import parseEmbedding


def test_none_embeddings_is_valid():
    # No embeddings provided is allowed (identity can be created without them).
    assert parseEmbedding(None) is True


def test_empty_list_is_valid():
    assert parseEmbedding([]) is True


def test_single_valid_512_vector():
    assert parseEmbedding([[0.0] * 512]) is True


def test_multiple_valid_vectors():
    assert parseEmbedding([[0.1] * 512, [0.2] * 512]) is True


def test_wrong_length_vector_is_invalid():
    assert parseEmbedding([[0.0] * 511]) is False


def test_too_long_vector_is_invalid():
    assert parseEmbedding([[0.0] * 513]) is False


def test_one_bad_vector_among_valid_ones_is_invalid():
    assert parseEmbedding([[0.0] * 512, [0.0] * 10]) is False
