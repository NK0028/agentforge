import os
import logging
import hashlib
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings

logger = logging.getLogger(__name__)

# ChromaDB persists to disk inside the project data directory
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(settings.WORKSPACE_DIR), "chromadb")
COLLECTION_NAME = "agentforge_knowledge"


def _get_client() -> chromadb.PersistentClient:
    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    return chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=ChromaSettings(anonymized_telemetry=False)
    )


def _get_collection():
    client = _get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


def _chunk_code(content: str, max_chars: int = 600) -> List[str]:
    """Split code into overlapping chunks for embedding."""
    lines = content.splitlines(keepends=True)
    chunks, current = [], ""
    for line in lines:
        current += line
        if len(current) >= max_chars:
            chunks.append(current.strip())
            # 20% overlap
            overlap_lines = lines[max(0, lines.index(line) - int(max_chars * 0.2 / 40)):]
            current = "".join(overlap_lines[:3])
    if current.strip():
        chunks.append(current.strip())
    return chunks or [content[:max_chars]]


class MemoryService:
    """
    ChromaDB-backed semantic memory and RAG knowledge base for AgentForge.

    Stores:
    - Generated code chunks per project (episodic memory).
    - Architectural patterns and framework snippets (semantic/shared memory).
    """

    def __init__(self):
        self.collection = _get_collection()

    def index_generated_files(self, project_id: str, files: List[Dict[str, str]]) -> int:
        """
        Index all generated code files from a completed project run.
        Returns the number of chunks stored.
        """
        docs, ids, metadatas = [], [], []

        for file_info in files:
            path    = file_info.get("path", "")
            content = file_info.get("content", "")
            if not content.strip():
                continue

            chunks = _chunk_code(content)
            for i, chunk in enumerate(chunks):
                chunk_id = hashlib.md5(f"{project_id}:{path}:{i}:{chunk[:50]}".encode()).hexdigest()
                docs.append(chunk)
                ids.append(chunk_id)
                metadatas.append({
                    "project_id": project_id,
                    "file_path":  path,
                    "chunk_index": i,
                    "memory_type": "episodic"
                })

        if docs:
            # Upsert avoids duplicates on re-runs
            self.collection.upsert(documents=docs, ids=ids, metadatas=metadatas)
            logger.info(f"Indexed {len(docs)} code chunks for project [{project_id}].")

        return len(docs)

    def store_pattern(self, pattern_id: str, title: str, content: str, tags: List[str] = []) -> None:
        """
        Store a reusable architectural pattern or best-practice snippet.
        These are shared across all project runs (semantic memory).
        """
        self.collection.upsert(
            documents=[content],
            ids=[f"pattern:{pattern_id}"],
            metadatas=[{
                "project_id":  "__shared__",
                "memory_type": "semantic",
                "title":       title,
                "tags":        ",".join(tags)
            }]
        )
        logger.info(f"Stored semantic pattern: [{title}]")

    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        project_id: Optional[str] = None,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic similarity search over the knowledge base.
        Optionally filter by project_id or memory_type.
        """
        where: Dict[str, Any] = {}
        if project_id and memory_type:
            where = {"$or": [
                {"project_id": project_id},
                {"memory_type": memory_type}
            ]}
        elif project_id:
            where = {"project_id": project_id}
        elif memory_type:
            where = {"memory_type": memory_type}

        try:
            kwargs: Dict[str, Any] = {
                "query_texts": [query],
                "n_results": min(n_results, self.collection.count() or 1)
            }
            if where:
                kwargs["where"] = where

            results = self.collection.query(**kwargs)

            hits = []
            docs      = results.get("documents", [[]])[0]
            metas     = results.get("metadatas",  [[]])[0]
            distances = results.get("distances",  [[]])[0]

            for doc, meta, dist in zip(docs, metas, distances):
                hits.append({
                    "content":    doc,
                    "metadata":   meta,
                    "similarity": round(1 - dist, 4)  # cosine: lower distance = higher similarity
                })
            return hits

        except Exception as e:
            logger.warning(f"RAG retrieval error: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Returns basic stats about the knowledge base."""
        try:
            count = self.collection.count()
        except Exception:
            count = 0
        return {
            "total_chunks": count,
            "persist_dir":  CHROMA_PERSIST_DIR,
            "collection":   COLLECTION_NAME
        }


# Singleton instance
memory_service = MemoryService()
