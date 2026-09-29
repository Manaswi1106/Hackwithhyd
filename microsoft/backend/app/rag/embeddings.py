"""
RAG Embeddings Layer
Provides dense vector embeddings for semantic document search.
"""

from typing import List
import hashlib
import math
import numpy as np


class EmbeddingsProvider:
    """Embeddings generator with deterministic fallback.
    Produces 384-dimensional dense vectors suitable for pgvector / cosine similarity.
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        """Generate a normalized embedding vector for a piece of text.
        Uses a hash-based bag-of-ngrams projection for zero-dependency determinism,
        ensuring fast, offline, and reliable vector similarity testing.
        """
        vector = np.zeros(self.dimension, dtype=np.float32)
        tokens = text.lower().split()
        if not tokens:
            return vector.tolist()

        for i, token in enumerate(tokens):
            # 1-gram
            h = int(hashlib.md5(token.encode('utf-8')).hexdigest(), 16)
            idx = h % self.dimension
            weight = 1.0 / (1.0 + 0.1 * i)
            vector[idx] += weight

            # 2-gram
            if i < len(tokens) - 1:
                bigram = f"{token}_{tokens[i+1]}"
                h2 = int(hashlib.sha256(bigram.encode('utf-8')).hexdigest(), 16)
                idx2 = h2 % self.dimension
                vector[idx2] += 1.5 * weight

        # L2 Normalize
        norm = np.linalg.norm(vector)
        if norm > 1e-6:
            vector = vector / norm

        return vector.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        a = np.array(v1, dtype=np.float32)
        b = np.array(v2, dtype=np.float32)
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a < 1e-6 or norm_b < 1e-6:
            return 0.0
        return float(dot / (norm_a * norm_b))
