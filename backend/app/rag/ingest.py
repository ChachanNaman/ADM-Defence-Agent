"""Chunk the fare rule corpus and (re)build the Chroma collection.

Run directly to (re)index: `python -m app.rag.ingest`
Chunking strategy: split each airline doc on level-2 headings ("## ...") —
each chunk is one fare-basis rule block. The document preamble (title, fare
basis legend, any reference tables) is prepended to every chunk from that
doc so a single retrieved chunk is self-contained enough for the LLM to
interpret the fare basis code without a second lookup.
"""

import re

from app.config import CHROMA_COLLECTION, FARE_RULES_DIR
from app.rag.embeddings import BGEEmbeddingFunction
from app.rag.store import _client

AIRLINE_BY_FILE_PREFIX = {
    "aa": "AA",
    "ey": "EY",
    "nh": "NH",
    "ai": "AI",
    "ek": "EK",
}

# First token of a "## " heading, e.g. "## Q7NR — Economy Value" -> "Q7NR"
_HEADING_CODE_RE = re.compile(r"^([A-Z0-9]{3,10})\b")


def _split_sections(doc_text: str) -> tuple[str, list[tuple[str, str]]]:
    parts = re.split(r"\n(?=## )", doc_text)
    preamble = parts[0]
    sections = []
    for part in parts[1:]:
        heading_line = part.splitlines()[0].removeprefix("## ").strip()
        sections.append((heading_line, part.strip()))
    return preamble.strip(), sections


def build_chunks() -> tuple[list[str], list[str], list[dict]]:
    ids, docs, metas = [], [], []

    for path in sorted(FARE_RULES_DIR.glob("*.md")):
        prefix = path.stem.split("_")[0]
        airline_code = AIRLINE_BY_FILE_PREFIX.get(prefix)
        if not airline_code:
            continue

        preamble, sections = _split_sections(path.read_text())
        for i, (heading, section_text) in enumerate(sections):
            match = _HEADING_CODE_RE.match(heading)
            fare_basis = match.group(1) if match else None

            chunk_text = f"{preamble}\n\n{section_text}"
            chunk_id = f"{airline_code}-{i}-{fare_basis or 'general'}"

            ids.append(chunk_id)
            docs.append(chunk_text)
            metas.append(
                {
                    "airline_code": airline_code,
                    "fare_basis": fare_basis or "",
                    "heading": heading,
                    "source": path.name,
                }
            )

    return ids, docs, metas


def ingest() -> int:
    client = _client()
    try:
        client.delete_collection(CHROMA_COLLECTION)
    except Exception:
        pass

    collection = client.create_collection(
        name=CHROMA_COLLECTION,
        embedding_function=BGEEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"},
    )

    ids, docs, metas = build_chunks()
    collection.add(ids=ids, documents=docs, metadatas=metas)
    return len(ids)


if __name__ == "__main__":
    n = ingest()
    print(f"Indexed {n} fare rule chunks into Chroma collection '{CHROMA_COLLECTION}'.")
