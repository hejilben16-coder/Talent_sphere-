"""ChromaDB persistent vector store: add, query, de-dup, and stats.

The collection is created with cosine space to match the normalized BGE
embeddings. File-level de-duplication is achieved by stamping every chunk's
metadata with the source file's sha256 hash; ingestion consults the set of
known hashes to skip files that were already indexed.
"""

from __future__ import annotations

import chromadb
import streamlit as st
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection

from src.config import CHROMA_COLLECTION, CHROMA_DB_PATH


@st.cache_resource(show_spinner=False)
def get_client() -> ClientAPI:
    """Return a cached, disk-persistent Chroma client."""
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)


def get_collection() -> Collection:
    """Return (creating if needed) the cosine-space document collection."""
    client = get_client()
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def ingested_hashes() -> set[str]:
    """Return the set of file hashes already present in the index."""
    collection = get_collection()
    try:
        result = collection.get(include=["metadatas"])
    except Exception:  # noqa: BLE001 - empty/new collection
        return set()

    hashes: set[str] = set()
    for meta in result.get("metadatas") or []:
        file_hash = (meta or {}).get("file_hash")
        if file_hash:
            hashes.add(file_hash)
    return hashes


def add_chunks(chunks: list[dict], embeddings: list[list[float]], file_hash: str) -> int:
    """Upsert chunks and their embeddings into the collection.

    Args:
        chunks: Chunk dicts from :func:`src.ingest.chunk_pages`.
        embeddings: Parallel list of embedding vectors.
        file_hash: sha256 of the source file, stamped on every chunk for de-dup.

    Returns:
        The number of chunks added.
    """
    if not chunks:
        return 0

    ids = [chunk["id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = []
    for chunk in chunks:
        meta = dict(chunk["metadata"])
        meta["file_hash"] = file_hash
        metadatas.append(meta)

    collection = get_collection()
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    return len(ids)


def search(query_embedding: list[float], top_k: int) -> list[dict]:
    """Run a cosine similarity search and return ranked results.

    Args:
        query_embedding: The query's embedding vector.
        top_k: Number of results to return.

    Returns:
        A list of ``{text, source, page, chunk_index, score}`` dicts sorted by
        descending similarity, where ``score = 1 - distance``.
    """
    collection = get_collection()
    if collection.count() == 0:
        return []

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]

    hits: list[dict] = []
    for text, meta, distance in zip(documents, metadatas, distances):
        meta = meta or {}
        hits.append(
            {
                "text": text,
                "source": meta.get("source", "unknown"),
                "page": meta.get("page", "—"),
                "chunk_index": meta.get("chunk_index", 0),
                "score": 1 - distance,
            }
        )

    hits.sort(key=lambda hit: hit["score"], reverse=True)
    return hits


def stats() -> dict:
    """Return index stats: total chunks and distinct source filenames."""
    collection = get_collection()
    total = collection.count()
    sources: set[str] = set()
    if total:
        try:
            result = collection.get(include=["metadatas"])
            for meta in result.get("metadatas") or []:
                source = (meta or {}).get("source")
                if source:
                    sources.add(source)
        except Exception:  # noqa: BLE001 - best-effort stats
            pass
    return {"total_chunks": total, "sources": len(sources), "source_names": sorted(sources)}


def reset_collection() -> None:
    """Delete and recreate the collection (clears the whole index)."""
    client = get_client()
    try:
        client.delete_collection(CHROMA_COLLECTION)
    except Exception:  # noqa: BLE001 - already absent
        pass
    client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )