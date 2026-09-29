"""
RAG Document Store & Chunker
Stores extracted text snippets, metadata, claims, and embeddings.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel
from .embeddings import EmbeddingsProvider


class DocumentChunk(BaseModel):
    id: str
    content: str
    source_url: Optional[str] = None
    title: Optional[str] = None
    retrieved_at: str
    claim: Optional[str] = None
    evidence_type: str = "observed"  # observed, inferred, modeled
    confidence: str = "medium"       # high, medium, low
    tags: List[str] = []
    embedding: Optional[List[float]] = None


class DocumentStore:
    """In-memory & pgvector compatible document store."""

    def __init__(self, embeddings: Optional[EmbeddingsProvider] = None):
        self.embeddings = embeddings or EmbeddingsProvider()
        self.chunks: Dict[str, DocumentChunk] = {}

    def add_document(
        self,
        content: str,
        source_url: Optional[str] = None,
        title: Optional[str] = None,
        claim: Optional[str] = None,
        evidence_type: str = "observed",
        confidence: str = "medium",
        tags: Optional[List[str]] = None,
        chunk_size: int = 400,
    ) -> List[str]:
        """Split content into overlapping chunks, compute embeddings, and store."""
        words = content.split()
        added_ids = []

        if len(words) <= chunk_size:
            chunk_texts = [content]
        else:
            step = int(chunk_size * 0.75)
            chunk_texts = [
                " ".join(words[i : i + chunk_size])
                for i in range(0, len(words), step)
            ]

        for text in chunk_texts:
            chunk_id = f"doc_{uuid.uuid4().hex[:12]}"
            emb = self.embeddings.embed_text(text)
            chunk = DocumentChunk(
                id=chunk_id,
                content=text,
                source_url=source_url,
                title=title,
                retrieved_at=datetime.now(timezone.utc).isoformat(),
                claim=claim,
                evidence_type=evidence_type,
                confidence=confidence,
                tags=tags or [],
                embedding=emb,
            )
            self.chunks[chunk_id] = chunk
            added_ids.append(chunk_id)

        return added_ids

    def get(self, chunk_id: str) -> Optional[DocumentChunk]:
        return self.chunks.get(chunk_id)
