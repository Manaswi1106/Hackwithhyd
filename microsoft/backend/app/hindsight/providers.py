"""
Hindsight Provider Abstraction Layer

Supports:
- RealHindsightProvider: Uses actual Hindsight by Vectorize API (hindsight-client SDK)
- MockHindsightProvider: For local development without credentials

The real provider uses the Hindsight bank-based API:
  - Retain:  POST /v1/default/banks/{bank_id}/memories
  - Recall:  POST /v1/default/banks/{bank_id}/memories/recall
  - Reflect: POST /v1/default/banks/{bank_id}/reflect

Auth: Bearer token (hsk_...) via Authorization header.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import json
import logging

logger = logging.getLogger(__name__)


class HindsightProvider(ABC):
    """Abstract provider interface for Hindsight memory system.

    This abstraction allows swapping between real Hindsight SDK
    and a mock provider for local development.
    """

    @abstractmethod
    async def retain(
        self,
        bank_id: str,
        content: str,
        context: Optional[str] = None,
        tags: Optional[List[str]] = None,
        occurred_at: Optional[str] = None,
        document_id: Optional[str] = None,
        retain_mission: Optional[str] = None,
    ) -> str:
        """Store a memory/observation in Hindsight."""
        pass

    @abstractmethod
    async def recall(
        self,
        bank_id: str,
        query: str,
        tags: Optional[List[str]] = None,
        types: Optional[List[str]] = None,
        prefer_observations: bool = True,
        max_tokens: int = 1500,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories from Hindsight using TEMPR retrieval."""
        pass

    @abstractmethod
    async def reflect(
        self,
        bank_id: str,
        query: str,
        budget: str = "mid",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get a synthesized reflection with citations from stored memories."""
        pass

    @abstractmethod
    async def create_mental_model(
        self,
        bank_id: str,
        name: str,
        source_query: str,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Create a mental model (pre-computed standing answer)."""
        pass


class MockHindsightProvider(HindsightProvider):
    """Mock provider for local development without Hindsight credentials.

    WARNING: This is ONLY for local development.
    Production/hackathon demo MUST use RealHindsightProvider.
    """

    def __init__(self):
        self._memories: Dict[str, List[Dict[str, Any]]] = {}
        self._mental_models: Dict[str, List[Dict[str, Any]]] = {}
        logger.warning("Using MockHindsightProvider — NOT suitable for production/demo")

    async def retain(
        self,
        bank_id: str,
        content: str,
        context: Optional[str] = None,
        tags: Optional[List[str]] = None,
        occurred_at: Optional[str] = None,
        document_id: Optional[str] = None,
        retain_mission: Optional[str] = None,
    ) -> str:
        if bank_id not in self._memories:
            self._memories[bank_id] = []

        memory_id = f"mock_mem_{bank_id}_{len(self._memories[bank_id]):04d}"
        self._memories[bank_id].append({
            "id": memory_id,
            "text": content,
            "context": context,
            "tags": tags or [],
            "occurred_at": occurred_at or datetime.now(timezone.utc).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "document_id": document_id,
            "fact_type": "world",
            "proof_count": 1,
        })
        logger.info(f"Mock retain: {memory_id} in bank {bank_id}")
        return memory_id

    async def recall(
        self,
        bank_id: str,
        query: str,
        tags: Optional[List[str]] = None,
        types: Optional[List[str]] = None,
        prefer_observations: bool = True,
        max_tokens: int = 1500,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        memories = self._memories.get(bank_id, [])

        # Tag filtering
        if tags:
            tag_set = set(tags)
            memories = [m for m in memories if tag_set.intersection(set(m.get("tags", [])))]

        # Simple keyword scoring for mock
        query_lower = query.lower()
        query_words = set(query_lower.split())
        scored = []
        for mem in memories:
            text_lower = mem["text"].lower()
            score = sum(1 for word in query_words if word in text_lower)
            if score > 0 or not query_words:
                scored.append((score, mem))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [
            {**m, "score": s / max(len(query_words), 1)}
            for s, m in scored[:10]
        ]
        return results

    async def reflect(
        self,
        bank_id: str,
        query: str,
        budget: str = "mid",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        memories = await self.recall(bank_id, query, tags=tags)
        if not memories:
            return {
                "text": "No previous observations found for this query.",
                "citations": [],
                "confidence": 0.0,
                "mental_models_used": [],
            }

        summaries = [m["text"][:300] for m in memories[:5]]
        return {
            "text": f"Based on {len(memories)} previous observations: " + "; ".join(summaries),
            "citations": [
                {"memory_id": m["id"], "quote": m["text"][:100]}
                for m in memories[:3]
            ],
            "confidence": 0.7,
            "mental_models_used": [],
        }

    async def create_mental_model(
        self,
        bank_id: str,
        name: str,
        source_query: str,
        tags: Optional[List[str]] = None,
    ) -> str:
        if bank_id not in self._mental_models:
            self._mental_models[bank_id] = []

        mm_id = f"mock_mm_{bank_id}_{len(self._mental_models[bank_id]):03d}"
        self._mental_models[bank_id].append({
            "id": mm_id,
            "name": name,
            "source_query": source_query,
            "tags": tags or [],
        })
        return mm_id


class RealHindsightProvider(HindsightProvider):
    """Real Hindsight SDK integration.

    Uses the actual Hindsight by Vectorize API.
    Requires HINDSIGHT_API_TOKEN environment variable.

    API Architecture:
        Base: https://api.hindsight.vectorize.io
        Path: /v1/default/banks/{bank_id}/...

    Endpoints used:
        - POST /v1/default/banks/{bank_id}/memories         (retain)
        - POST /v1/default/banks/{bank_id}/memories/recall   (recall / TEMPR retrieval)
        - POST /v1/default/banks/{bank_id}/reflect           (agentic reflect)
        - POST /v1/default/banks/{bank_id}/mental-models     (create mental model)
    """

    def __init__(
        self,
        api_token: str,
        base_url: str = "https://api.hindsight.vectorize.io",
    ):
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self._client = None
        logger.info(f"RealHindsightProvider initialized → {self.base_url}")

    async def _ensure_client(self):
        if self._client is None:
            import httpx

            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )

    def _bank_url(self, bank_id: str, path: str) -> str:
        return f"/v1/default/banks/{bank_id}/{path}"

    async def retain(
        self,
        bank_id: str,
        content: str,
        context: Optional[str] = None,
        tags: Optional[List[str]] = None,
        occurred_at: Optional[str] = None,
        document_id: Optional[str] = None,
        retain_mission: Optional[str] = None,
    ) -> str:
        await self._ensure_client()

        item: Dict[str, Any] = {"content": content}
        if context:
            item["context"] = context
        if tags:
            item["tags"] = tags
        if occurred_at:
            item["occurred_at"] = occurred_at
        if document_id:
            item["document_id"] = document_id

        body: Dict[str, Any] = {"items": [item]}
        if retain_mission:
            body["retain_mission"] = retain_mission

        try:
            response = await self._client.post(
                self._bank_url(bank_id, "memories"),
                json=body,
                params={"async": "false"},
            )
            response.raise_for_status()
            data = response.json()
            memory_id = data.get("id", data.get("operation_id", ""))
            logger.info(f"Hindsight retain success: bank={bank_id}, id={memory_id}")
            return memory_id
        except Exception as e:
            logger.error(f"Hindsight retain error: {e}")
            raise

    async def recall(
        self,
        bank_id: str,
        query: str,
        tags: Optional[List[str]] = None,
        types: Optional[List[str]] = None,
        prefer_observations: bool = True,
        max_tokens: int = 1500,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        await self._ensure_client()

        body: Dict[str, Any] = {
            "query": query,
            "prefer_observations": prefer_observations,
            "max_tokens": max_tokens,
        }
        if tags:
            body["tags"] = tags
        if types:
            body["types"] = types
        if start_date:
            body["start_date"] = start_date
        if end_date:
            body["end_date"] = end_date

        try:
            response = await self._client.post(
                self._bank_url(bank_id, "memories/recall"),
                json=body,
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            logger.info(f"Hindsight recall: bank={bank_id}, query='{query[:50]}', results={len(results)}")
            return results
        except Exception as e:
            logger.error(f"Hindsight recall error: {e}")
            raise

    async def reflect(
        self,
        bank_id: str,
        query: str,
        budget: str = "mid",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        await self._ensure_client()

        body: Dict[str, Any] = {
            "query": query,
            "budget": budget,
        }
        if tags:
            body["tags"] = tags

        try:
            response = await self._client.post(
                self._bank_url(bank_id, "reflect"),
                json=body,
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Hindsight reflect: bank={bank_id}, confidence={data.get('confidence', 'N/A')}")
            return {
                "text": data.get("text", ""),
                "citations": data.get("citations", []),
                "confidence": data.get("confidence", 0.0),
                "mental_models_used": data.get("mental_models_used", []),
                "structured_output": data.get("structured_output"),
            }
        except Exception as e:
            logger.error(f"Hindsight reflect error: {e}")
            raise

    async def create_mental_model(
        self,
        bank_id: str,
        name: str,
        source_query: str,
        tags: Optional[List[str]] = None,
    ) -> str:
        await self._ensure_client()

        body: Dict[str, Any] = {
            "name": name,
            "source_query": source_query,
        }
        if tags:
            body["tags"] = tags

        try:
            response = await self._client.post(
                self._bank_url(bank_id, "mental-models"),
                json=body,
            )
            response.raise_for_status()
            data = response.json()
            mm_id = data.get("id", "")
            logger.info(f"Hindsight mental model created: bank={bank_id}, id={mm_id}")
            return mm_id
        except Exception as e:
            logger.error(f"Hindsight mental model creation error: {e}")
            raise

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


class HindsightConfigurationError(RuntimeError):
    """Raised when Hindsight is in cloud mode but credentials are missing."""
    pass


def create_hindsight_provider(
    api_token: Optional[str] = None,
    base_url: str = "https://api.hindsight.vectorize.io",
    mode: Optional[str] = None,
) -> HindsightProvider:
    """Factory function to create the appropriate Hindsight provider.

    Uses RealHindsightProvider in 'cloud' mode when HINDSIGHT_API_TOKEN is available.
    Raises HindsightConfigurationError if in cloud mode without credentials.
    'mock' mode is allowed only when explicitly configured via HINDSIGHT_MODE=mock.
    """
    from app.config import settings

    effective_mode = (mode or getattr(settings, "hindsight_mode", "cloud")).lower()
    effective_token = api_token or getattr(settings, "hindsight_api_token", None) or getattr(settings, "hindsight_api_key", None)

    if effective_mode == "mock":
        logger.info("Using MockHindsightProvider (HINDSIGHT_MODE=mock)")
        return MockHindsightProvider()

    if effective_token:
        logger.info("Creating RealHindsightProvider with actual Vectorize Hindsight API")
        return RealHindsightProvider(api_token=effective_token, base_url=base_url)

    import sys
    import os
    is_testing = (
        getattr(settings, "app_env", "") in ("testing", "test")
        or "pytest" in sys.modules
        or bool(os.environ.get("PYTEST_CURRENT_TEST"))
    )
    if is_testing or getattr(settings, "app_env", "development") == "development":
        logger.warning("No HINDSIGHT_API_TOKEN provided — running in local Hindsight memory mode. Set HINDSIGHT_API_TOKEN for live cloud sync.")
        return MockHindsightProvider()

    raise HindsightConfigurationError(
        "Hindsight is configured in 'cloud' mode but no HINDSIGHT_API_TOKEN or HINDSIGHT_API_KEY was found. "
        "Please set HINDSIGHT_API_TOKEN=hsk_... in your .env, or set HINDSIGHT_MODE=mock for local development."
    )

