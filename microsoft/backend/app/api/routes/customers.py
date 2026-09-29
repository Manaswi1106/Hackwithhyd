"""
Customers API Routes
Endpoints for exploring target customer segments, purchase behavior, and funnel metrics.
"""

from fastapi import APIRouter
from app.agents.customer_agent import CustomerIntelligenceAgent

router = APIRouter()
customer_agent = CustomerIntelligenceAgent()


@router.get("/{market_id}/segments")
async def get_customer_segments(market_id: str):
    """Retrieve modeled customer segments and funnel conversion stages."""
    data = await customer_agent.analyze_customer_demand(
        category="Fashion & Lifestyle",
        subcategory="Footwear",
    )
    return {"success": True, "market_id": market_id, "data": data}
