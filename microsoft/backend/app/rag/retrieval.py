"""
RAG Retrieval Layer
Performs semantic & hybrid search over stored evidence chunks.
"""

from typing import List, Dict, Any, Optional
from .document_store import DocumentStore, DocumentChunk
from .embeddings import EmbeddingsProvider


class RAGRetriever:
    def __init__(self, store: DocumentStore):
        self.store = store
        self.embeddings = store.embeddings

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_tags: Optional[List[str]] = None,
        min_similarity: float = 0.1,
    ) -> List[Dict[str, Any]]:
        """Retrieve top-k relevant document chunks for a given query."""
        if not self.store.chunks:
            return []

        query_vec = self.embeddings.embed_text(query)
        scored_chunks = []

        query_terms = set(query.lower().split())

        for chunk in self.store.chunks.values():
            # Check tag filters
            if filter_tags:
                if not any(t in chunk.tags for t in filter_tags):
                    continue

            # Semantic similarity
            sem_score = 0.0
            if chunk.embedding:
                sem_score = self.embeddings.cosine_similarity(query_vec, chunk.embedding)

            # Keyword lexical overlap
            chunk_terms = set(chunk.content.lower().split())
            lex_score = len(query_terms.intersection(chunk_terms)) / max(len(query_terms), 1)

            # Hybrid score: 70% semantic + 30% lexical
            total_score = 0.7 * sem_score + 0.3 * lex_score

            if total_score >= min_similarity:
                scored_chunks.append((total_score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, chunk in scored_chunks[:top_k]:
            results.append({
                "id": chunk.id,
                "content": chunk.content,
                "source_url": chunk.source_url,
                "title": chunk.title,
                "claim": chunk.claim,
                "evidence_type": chunk.evidence_type,
                "confidence": chunk.confidence,
                "retrieved_at": chunk.retrieved_at,
                "relevance_score": round(score, 4),
            })

        return results
