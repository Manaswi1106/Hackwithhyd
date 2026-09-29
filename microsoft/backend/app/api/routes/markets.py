"""
Market API Routes
Endpoints for empirical market intelligence, Top 5 location recommendations,
weighted multi-factor rankings, and Hindsight memory adjustments.
All values dynamically loaded from CSV datasets.
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from app.services.market_intelligence_engine import MarketIntelligenceEngine
from app.services.data_loader import MarketDataLoader
from app.trajectory.engine import TrajectoryEngine, TrajectoryAssumptions

router = APIRouter()

class MarketRecommendationRequest(BaseModel):
    category: str = Field(default="Specialty Coffee", description="Venture category")
    customer_segment: str = Field(default="Tech Professionals", description="Primary customer demographic")
    store_size: float = Field(default=1200.0, description="Store area in sqft")
    budget: float = Field(default=3000000.0, description="Available capex/investment budget")
    city: str = Field(default="Hyderabad", description="Target city")


@router.post("/recommendations")
async def get_market_recommendations(payload: MarketRecommendationRequest):
    """Generate Top 5 ranked commercial locations using 6-factor weighted scoring + Hindsight memory modifier."""
    evaluation = MarketIntelligenceEngine.evaluate_markets(
        category=payload.category,
        customer_segment=payload.customer_segment,
        store_size=payload.store_size,
        budget=payload.budget,
        city=payload.city,
    )
    return {
        "success": True,
        "data": evaluation
    }


@router.get("/recommendations")
async def get_market_recommendations_get(
    category: str = Query(default="Specialty Coffee"),
    customer_segment: str = Query(default="Tech Professionals"),
    store_size: float = Query(default=1200.0),
    budget: float = Query(default=3000000.0),
    city: str = Query(default="Hyderabad"),
):
    """GET variant of market recommendations."""
    evaluation = MarketIntelligenceEngine.evaluate_markets(
        category=category,
        customer_segment=customer_segment,
        store_size=store_size,
        budget=budget,
        city=city,
    )
    return {
        "success": True,
        "data": evaluation
    }


@router.get("/{id}/overview")
async def get_market_overview(
    id: str,
    category: Optional[str] = None,
    customer_segment: Optional[str] = None,
    store_size: Optional[float] = 1200.0,
):
    """Retrieve complete Market Overview data pack loaded dynamically from CSV datasets."""
    cat = category or "Specialty Coffee"
    if not category:
        if "coffee" in id.lower():
            cat = "Specialty Coffee"
        elif "footwear" in id.lower():
            cat = "Footwear"
        elif "fashion" in id.lower():
            cat = "Fashion Retail"
        elif "restaurant" in id.lower() or "food" in id.lower():
            cat = "Restaurant"

    seg = customer_segment or "Tech Professionals"
    evaluation = MarketIntelligenceEngine.evaluate_markets(
        category=cat,
        customer_segment=seg,
        store_size=store_size or 1200.0,
        city="Hyderabad",
    )

    engine = TrajectoryEngine(TrajectoryAssumptions())
    scenarios = engine.generate_all_scenarios(months=24)

    return {
        "success": True,
        "data": {
            "market_id": id,
            "city": "Hyderabad",
            "category": cat,
            "customer_segment": seg,
            "top_5": evaluation["top_5"],
            "all_localities": evaluation["all_ranked"],
            "localities": evaluation["all_ranked"],
            "localities_count": len(evaluation["all_ranked"]),
            "hindsight_insight": evaluation["hindsight_insight"],
            "why_this_location": evaluation["why_this_location"],
            "why_not_others": evaluation["why_not_others"],
            "trajectory": {
                "scenarios": scenarios,
                "drivers": scenarios.get("drivers", []),
            },
            "evidence_summary": {
                "total_localities_calibrated": len(evaluation["all_ranked"]),
                "primary_evidence_sources": [
                    "Empirical Locality Dataset (areas.csv)",
                    "Historical Commercial Sales Register (historical_sales.csv)",
                    "Competitor Registry (competitor_reference.csv)",
                    "Hindsight Continuous Memory Bank"
                ],
                "confidence": "High",
                "classification": "Empirically Calibrated Market Model"
            }
        }
    }


@router.get("/{id}/localities/{locality_id}")
async def get_locality_detail_endpoint(id: str, locality_id: str):
    """Retrieve detailed empirical record for a specific locality."""
    areas = MarketDataLoader.load_areas()
    match = next((a for a in areas if a["area"].lower() == locality_id.lower()), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Locality '{locality_id}' not found.")
    return {"success": True, "data": match}


@router.get("/{id}/map")
async def get_market_map(id: str, category: Optional[str] = None):
    """Retrieve locality-level geographic heatmap signals and geo-coordinates."""
    areas = MarketDataLoader.load_areas()
    return {
        "success": True,
        "data": {
            "city": "Hyderabad",
            "locations": areas,
            "default_center": {"lat": 17.4401, "lng": 78.3489},
            "default_zoom": 12,
        }
    }
