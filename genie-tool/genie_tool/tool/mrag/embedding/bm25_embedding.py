from fastembed import SparseTextEmbedding


class BM25Embedding:
    def __init__(self):
        self._model = SparseTextEmbedding("Qdrant/bm25")

    def encode_text_batch(self, texts: list[str]) -> list[dict]:
        embeddings = self._model.embed(texts)
        return [embedding.as_object() for embedding in embeddings]


def get_bm25_embedding_model() -> BM25Embedding:
    return BM25Embedding()
