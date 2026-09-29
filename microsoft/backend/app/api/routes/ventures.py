"""
Ventures API Routes
Endpoints for venture URL deep inspection, domain classification, Venture X-Ray,
category mismatch detection, and Hindsight longitudinal tracking.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import re

from app.agents.venture_agent import VentureAnalysisAgent
from app.agents.retail_classifier import RetailWebsiteClassifierAgent, NON_RETAIL_MESSAGE
from app.hindsight.memory_service import HindsightMemoryService
from app.hindsight.providers import create_hindsight_provider
from app.config import settings

router = APIRouter()
venture_agent = VentureAnalysisAgent()
retail_classifier = RetailWebsiteClassifierAgent()

provider = create_hindsight_provider(
    api_token=settings.hindsight_api_token,
    base_url=settings.hindsight_api_url,
)
hindsight_service = HindsightMemoryService(
    provider=provider,
    bank_id=settings.hindsight_bank_id,
)


class ClassifyUrlRequest(BaseModel):
    url: str
    category: Optional[str] = None
    venture_name: Optional[str] = None


class AnalyzeVentureRequest(BaseModel):
    url: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None


@router.post("/classify")
async def classify_retail_url(payload: ClassifyUrlRequest):
    """Classify website URL into retail vs non-retail using Groq reasoning agent with domain validation."""
    result = await retail_classifier.classify_url(
        url=payload.url,
        selected_category=payload.category,
        venture_name=payload.venture_name
    )
    if not result.get("retail_status", False):
        return {
            "success": False,
            "retail_status": False,
            "error_type": result.get("error_type", "Validation Error"),
            "message": result.get("message", "Website classification failed."),
            "data": result,
        }
    return {
        "success": True,
        "retail_status": True,
        "data": result,
    }


def _clean_venture_id(url_or_name: str) -> str:
    """Produce a safe venture identifier for Hindsight memory tags."""
    cleaned = re.sub(r'https?://', '', url_or_name.lower())
    cleaned = re.sub(r'[^\w\-]', '_', cleaned).strip('_')
    return cleaned[:40] if cleaned else "unknown_venture"


@router.post("/analyze")
async def analyze_venture(payload: AnalyzeVentureRequest):
    """Inspect a venture URL and generate a Venture X-Ray profile with domain validation."""
    if payload.url:
        classification = await retail_classifier.classify_url(payload.url)
        if not classification.get("retail_status", False):
            return {
                "success": False,
                "retail_status": False,
                "message": classification.get("message", NON_RETAIL_MESSAGE),
                "data": {
                    "classification": classification,
                    "pipeline_status": "rejected_non_retail",
                }
            }
        if not payload.name and classification.get("business_name"):
            payload.name = classification["business_name"]
        if not payload.subcategory and classification.get("category"):
            payload.subcategory = classification["category"]
    analysis = await venture_agent.analyze_venture(
        venture_url=payload.url,
        venture_name=payload.name,
        category=payload.category,
        subcategory=payload.subcategory,
    )

    # Hindsight Memory Integration
    hindsight_info: Dict[str, Any] = {
        "remembered": False,
        "previous_memory_found": False,
        "longitudinal_note": None,
    }

    if payload.url or payload.name:
        v_id = _clean_venture_id(payload.url or payload.name or "venture")
        try:
            # 1. Recall prior memories
            prior_memories = await hindsight_service.recall_venture_context(
                venture_id=v_id,
                query="Previous venture analysis, business model, price, positioning, domain",
            )

            if prior_memories:
                hindsight_info["previous_memory_found"] = True
                hindsight_info["prior_count"] = len(prior_memories)
                hindsight_info["latest_prior_snippet"] = prior_memories[0].get("text", "")[:200]
                hindsight_info["longitudinal_note"] = (
                    f"Hindsight retrieved {len(prior_memories)} prior observation(s) for this venture. "
                    f"Tracked changes are preserved across runs."
                )

            # 2. Retain current analysis snapshot
            xray = analysis.get("xray", {})
            classification = analysis.get("classification", {})
            await hindsight_service.remember_venture_analysis(
                venture_id=v_id,
                analysis={
                    "name": analysis.get("name", "Unknown"),
                    "url": payload.url,
                    "domain": classification.get("primary_domain", "unknown"),
                    "sub_domain": classification.get("sub_domain", ""),
                    "business_model": xray.get("business_model", {}).get("value", "N/A"),
                    "price": xray.get("price", {}).get("value", "N/A"),
                    "positioning": xray.get("positioning", {}).get("value", "N/A"),
                    "target_audience": xray.get("target_audience", {}).get("value", "N/A"),
                    "differentiators": xray.get("differentiators", []),
                    "competitive_overlap": xray.get("competitive_overlap", []),
                    "strengths": xray.get("strength_signals", []),
                    "risks": xray.get("risk_signals", []),
                }
            )
            hindsight_info["remembered"] = True
        except Exception as e:
            hindsight_info["error"] = str(e)[:100]

    analysis["hindsight"] = hindsight_info
    return {"success": True, "data": analysis}


@router.get("/{id}")
async def get_venture(id: str):
    """Retrieve venture metadata."""
    analysis = await venture_agent.analyze_venture(
        venture_name=id.replace('_', ' ').title(),
    )
    return {"success": True, "data": analysis}


@router.get("/{id}/xray")
async def get_venture_xray(id: str):
    """Retrieve Venture X-Ray signals."""
    analysis = await venture_agent.analyze_venture(
        venture_name=id.replace('_', ' ').title(),
    )
    return {"success": True, "data": analysis["xray"]}
