"""
Maps API Routes
Endpoints for market opportunity heatmaps and geographic locality signals.
"""

from fastapi import APIRouter
from app.agents.market_agent import MarketResearchAgent

router = APIRouter()
market_agent = MarketResearchAgent()


@router.get("/{market_id}/heatmap")
async def get_heatmap_data(market_id: str):
    """Retrieve geographic market signals for map layers."""
    data = await market_agent.analyze_market("Hyderabad", "Fashion & Lifestyle", "Footwear")
    return {
        "success": True,
        "market_id": market_id,
        "data": {
            "city": "Hyderabad",
            "locations": data["top_locations"],
            "default_center": {"lat": 17.4401, "lng": 78.3489},
            "default_zoom": 12,
        }
    }
