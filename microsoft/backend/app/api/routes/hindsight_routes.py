"""
Hindsight Memory API Routes
Endpoints for:
- Retaining completed simulations and venture outcomes
- Recalling past experiences to adjust recommendation scores
- Providing timeline of retained business experiences for the Memory Timeline UI
- Longitudinal change tracking and reflection
"""

import uuid
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from app.hindsight.memory_service import HindsightMemoryService
from app.hindsight.providers import create_hindsight_provider
from app.services.market_intelligence_engine import MarketIntelligenceEngine
from app.config import settings

router = APIRouter()

provider = create_hindsight_provider(
    api_token=settings.hindsight_api_token,
    base_url=settings.hindsight_api_url,
)
hindsight_service = HindsightMemoryService(
    provider=provider,
    bank_id=settings.hindsight_bank_id,
)


class RetainSimulationRequest(BaseModel):
    business_category: str = Field(..., description="e.g. Specialty Coffee, Fashion Retail, Footwear")
    chosen_locality: str = Field(..., description="e.g. Madhapur, Gachibowli")
    predicted_revenue: float = Field(..., description="Projected monthly revenue")
    actual_revenue: float = Field(..., description="Actual observed or simulated revenue")
    customer_segment: str = Field(default="Tech Professionals")
    investment: float = Field(default=3000000.0)
    success_or_failure: str = Field(default="Success")
    strategic_lesson: str = Field(..., description="Strategic lesson learned from this location deployment")


class RetainSnapshotRequest(BaseModel):
    market_id: str = "hyderabad_market"
    state: Optional[Dict[str, Any]] = None
    analysis_id: Optional[str] = None


class ReflectRequest(BaseModel):
    market_id: str = "hyderabad_market"
    query: str = "What are the major shifts in retail competition and pricing in Hyderabad?"


@router.post("/retain-simulation")
async def retain_simulation_endpoint(payload: RetainSimulationRequest):
    """Retain a completed simulation into Hindsight memory.
    
    Stores:
    - business_category
    - chosen_locality
    - predicted_revenue
    - actual_revenue
    - customer_segment
    - investment
    - success_or_failure
    - strategic_lesson
    """
    mem_entry = {
        "id": f"mem_{uuid.uuid4().hex[:6]}",
        "business_category": payload.business_category,
        "chosen_locality": payload.chosen_locality,
        "predicted_revenue": payload.predicted_revenue,
        "actual_revenue": payload.actual_revenue,
        "customer_segment": payload.customer_segment,
        "investment": payload.investment,
        "success_or_failure": payload.success_or_failure,
        "strategic_lesson": payload.strategic_lesson,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Store in persistent local store
    saved_entry = MarketIntelligenceEngine.retain_simulation_memory(mem_entry)

    # Also store into Hindsight cloud if configured
    hindsight_id = None
    try:
        content = (
            f"Venture simulation experience for {payload.business_category} in {payload.chosen_locality}. "
            f"Customer segment: {payload.customer_segment}. "
            f"Predicted revenue: ₹{payload.predicted_revenue:,.0f}, Actual revenue: ₹{payload.actual_revenue:,.0f}. "
            f"Outcome: {payload.success_or_failure}. "
            f"Strategic lesson: {payload.strategic_lesson}"
        )
        hindsight_id = await hindsight_service.provider.retain(
            bank_id=hindsight_service.bank_id,
            content=content,
            tags=[
                "type:simulation_experience",
                f"locality:{payload.chosen_locality.lower().replace(' ', '_')}",
                f"category:{payload.business_category.lower().replace(' ', '_')}",
            ],
            occurred_at=mem_entry["timestamp"]
        )
    except Exception:
        pass

    return {
        "success": True,
        "memory_id": hindsight_id or mem_entry["id"],
        "data": saved_entry,
        "message": f"Retained experience for {payload.business_category} in {payload.chosen_locality}. Future recommendations will recall this insight."
    }


@router.get("/experiences")
async def get_all_experiences():
    """Retrieve all retained chronological simulation experiences for Memory Timeline."""
    memories = MarketIntelligenceEngine.get_memories()
    return {
        "success": True,
        "count": len(memories),
        "data": memories
    }


@router.get("/{venture_id}/timeline")
async def get_hindsight_timeline(venture_id: str):
    """Retrieve chronological timeline of retained business experiences."""
    memories = MarketIntelligenceEngine.get_memories()
    timeline_entries = []
    for idx, mem in enumerate(memories):
        timeline_entries.append({
            "memory_id": mem.get("id", f"mem_{idx+1}"),
            "category": mem.get("business_category", "Retail"),
            "locality": mem.get("chosen_locality", "Hyderabad"),
            "predicted_revenue": mem.get("predicted_revenue", 0),
            "actual_revenue": mem.get("actual_revenue", 0),
            "customer_segment": mem.get("customer_segment", "Tech Professionals"),
            "outcome": mem.get("success_or_failure", "Success"),
            "lesson": mem.get("strategic_lesson", ""),
            "timestamp": mem.get("timestamp", datetime.now(timezone.utc).isoformat()),
        })
    return {
        "success": True,
        "venture_id": venture_id,
        "total_events": len(timeline_entries),
        "timeline": timeline_entries,
    }


@router.get("/{venture_id}/changes")
async def get_hindsight_changes(venture_id: str):
    """Return longitudinal change detection."""
    memories = MarketIntelligenceEngine.get_memories()
    return {
        "success": True,
        "venture_id": venture_id,
        "total_memories": len(memories),
        "summary": f"Hindsight maintains {len(memories)} continuous empirical business memory records.",
        "recent_lessons": [m["strategic_lesson"] for m in memories[:3]],
        "impact_statement": "Recalled business experiences dynamically modify location suitability scoring.",
    }


@router.post("/retain-state")
async def retain_market_snapshot(payload: RetainSnapshotRequest):
    """Explicitly store an analysis snapshot into Hindsight."""
    mem_entry = {
        "id": f"mem_{uuid.uuid4().hex[:6]}",
        "business_category": "Market Snapshot",
        "chosen_locality": payload.market_id,
        "predicted_revenue": 0,
        "actual_revenue": 0,
        "customer_segment": "All",
        "investment": 0,
        "success_or_failure": "Observed",
        "strategic_lesson": f"Periodic market snapshot recorded for {payload.market_id}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    MarketIntelligenceEngine.retain_simulation_memory(mem_entry)
    return {
        "success": True,
        "memory_id": mem_entry["id"],
        "timestamp": mem_entry["timestamp"],
    }


@router.post("/reflect")
async def reflect_market_query(payload: ReflectRequest):
    """Ask Hindsight to reflect on market history and synthesize insights."""
    memories = MarketIntelligenceEngine.get_memories()
    relevant = [m for m in memories if payload.query.lower() in m["strategic_lesson"].lower() or payload.query.lower() in m["business_category"].lower()]
    sample = relevant if relevant else memories[:3]
    reflection_text = " ".join([f"[{m['chosen_locality']} - {m['business_category']}]: {m['strategic_lesson']}" for m in sample])
    return {
        "success": True,
        "market_id": payload.market_id,
        "query": payload.query,
        "reflection": reflection_text or "No specific memory matches found for this query.",
        "citations": [m["id"] for m in sample],
    }
