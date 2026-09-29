"""
Research Service
High-level service coordinating research tasks across agents and the document store.
"""

from typing import Dict, Any, Optional
from app.agents.orchestrator import VentureScopeOrchestrator
from app.rag.document_store import DocumentStore
from app.rag.retrieval import RAGRetriever


class ResearchService:
    def __init__(self, orchestrator: Optional[VentureScopeOrchestrator] = None):
        self.orchestrator = orchestrator or VentureScopeOrchestrator()
        self.doc_store = DocumentStore()
        self.retriever = RAGRetriever(self.doc_store)

    async def execute_research(
        self,
        city: str = "Hyderabad",
        category: str = "Fashion & Lifestyle",
        subcategory: str = "Footwear",
        venture_url: Optional[str] = None,
        venture_name: Optional[str] = None,
        deployment_model: str = "hybrid",
        target_location: str = "Gachibowli",
        what_if_overrides: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Execute full research pipeline and index key evidence chunks."""
        result = await self.orchestrator.run_full_pipeline(
            city=city,
            category=category,
            subcategory=subcategory,
            venture_url=venture_url,
            venture_name=venture_name,
            deployment_model=deployment_model,
            target_location=target_location,
            what_if_overrides=what_if_overrides,
        )

        # Index research into local RAG store for quick semantic search
        for comp in result.get("competitors", []):
            self.doc_store.add_document(
                content=f"{comp['name']} operates in {subcategory} with prices ₹{comp['price_range']['min']} - ₹{comp['price_range']['max']} positioned as {comp['positioning']}.",
                title=comp['name'],
                claim=f"Competitor profile for {comp['name']}",
                evidence_type="observed",
                confidence="high",
                tags=["competitor", comp['name'].lower()],
            )

        return result
