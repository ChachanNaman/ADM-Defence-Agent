"""Local BGE embeddings (via fastembed) wrapped as a Chroma EmbeddingFunction.

Runs fully offline after the first model download — no external embedding API,
matching the PRD's "local, zero infrastructure" requirement for the RAG store.
"""

from typing import Any

from chromadb.api.types import Documents, Embeddings

from app.config import EMBEDDING_MODEL

# BGE models are trained with an instruction prefix on the query side only;
# document/passage text is embedded as-is.
_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

_model = None


def _get_model():
    global _model
    if _model is None:
        from fastembed import TextEmbedding

        _model = TextEmbedding(model_name=EMBEDDING_MODEL)
    return _model


class BGEEmbeddingFunction:
    """Chroma EmbeddingFunction backed by fastembed's local BGE-small model."""

    def __init__(self, model_name: str = EMBEDDING_MODEL) -> None:
        self.model_name = model_name

    def __call__(self, input: Documents) -> Embeddings:
        model = _get_model()
        return [list(vec) for vec in model.embed(list(input))]

    def embed_query(self, input: Documents) -> Embeddings:
        model = _get_model()
        prefixed = [f"{_QUERY_PREFIX}{text}" for text in input]
        return [list(vec) for vec in model.embed(prefixed)]

    @staticmethod
    def name() -> str:
        return "bge_fastembed"

    def get_config(self) -> dict[str, Any]:
        return {"model_name": self.model_name}

    @staticmethod
    def build_from_config(config: dict[str, Any]) -> "BGEEmbeddingFunction":
        return BGEEmbeddingFunction(model_name=config.get("model_name", EMBEDDING_MODEL))

    def default_space(self) -> str:
        return "cosine"
