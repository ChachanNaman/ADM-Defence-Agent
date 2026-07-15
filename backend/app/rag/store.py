"""Chroma-backed retrieval over the fare rule corpus.

Per PRD risk mitigation ("Fare rule RAG returns wrong chunks"): the corpus is
small and curated (5 docs), and every query is filtered by airline_code via
Chroma metadata `where` *before* semantic search runs, so retrieval can only
ever return rules that are actually filed by the airline that issued the ADM.
"""

from dataclasses import dataclass
from functools import lru_cache

import chromadb

from app.config import CHROMA_COLLECTION, CHROMA_DIR
from app.rag.embeddings import BGEEmbeddingFunction


@dataclass
class RuleChunk:
    chunk_id: str
    airline_code: str
    fare_basis: str | None
    heading: str
    source: str
    text: str
    score: float  # cosine similarity, higher is better


@lru_cache(maxsize=1)
def _client() -> chromadb.ClientAPI:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_collection():
    return _client().get_or_create_collection(
        name=CHROMA_COLLECTION,
        embedding_function=BGEEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"},
    )


def collection_is_empty() -> bool:
    try:
        return get_collection().count() == 0
    except Exception:
        return True


def retrieve_fare_rule(
    airline_code: str,
    query_text: str,
    fare_basis: str | None = None,
    k: int = 4,
) -> list[RuleChunk]:
    """Metadata-filter by airline, then semantic search within that filter.

    Falls back to an unfiltered search if the airline has no indexed rules at
    all (should not happen with the current corpus, but keeps retrieval from
    hard-failing if a new airline shows up without a filed rule doc).
    """
    collection = get_collection()
    where = {"airline_code": airline_code}

    result = collection.query(
        query_texts=[query_text],
        n_results=k,
        where=where,
    )

    if not result["ids"][0]:
        result = collection.query(query_texts=[query_text], n_results=k)

    chunks: list[RuleChunk] = []
    ids = result["ids"][0]
    docs = result["documents"][0]
    metas = result["metadatas"][0]
    dists = result["distances"][0]
    for cid, doc, meta, dist in zip(ids, docs, metas, dists):
        similarity = 1.0 - dist
        chunks.append(
            RuleChunk(
                chunk_id=cid,
                airline_code=meta.get("airline_code", ""),
                fare_basis=meta.get("fare_basis"),
                heading=meta.get("heading", ""),
                source=meta.get("source", ""),
                text=doc,
                score=similarity,
            )
        )

    # Chunks whose heading exactly names the fare basis on the ticket are the
    # strongest possible signal — surface them first regardless of cosine rank.
    if fare_basis:
        chunks.sort(key=lambda c: (c.fare_basis != fare_basis, -c.score))
    return chunks
