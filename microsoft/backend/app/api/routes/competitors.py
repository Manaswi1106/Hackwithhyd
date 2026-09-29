"""
Competitors API Routes
Live Google Places Competitor Intelligence with Saturation Analysis.
Explicitly labels 'DEMO DATA' if Google Maps API is unavailable.
"""

from fastapi import APIRouter, Query
from typing import Optional, Dict, Any
from app.services.google_places_service import GooglePlacesService
from app.services.data_loader import MarketDataLoader

router = APIRouter()
places_service = GooglePlacesService()

@router.get("/nearby")
async def get_nearby_competitors_endpoint(
    locality: Optional[str] = Query(default="Madhapur"),
    category: Optional[str] = Query(default="Specialty Coffee"),
    lat: Optional[float] = Query(default=None),
    lng: Optional[float] = Query(default=None),
    radius: Optional[int] = Query(default=3000),
):
    """Retrieve live or calibrated competitor establishments with saturation rating."""
    target_lat = lat
    target_lng = lng
    
    if target_lat is None or target_lng is None:
        areas = MarketDataLoader.load_areas()
        match = next((a for a in areas if a["area"].lower() == (locality or "").lower()), None)
        if match:
            target_lat = match["lat"]
            target_lng = match["lng"]
        else:
            target_lat = 17.4484
            target_lng = 78.3908

    result = await places_service.get_nearby_competitors(
        lat=target_lat,
        lng=target_lng,
        category=category or "Specialty Coffee",
        radius_meters=radius or 3000,
        locality_name=locality
    )
    return {
        "success": True,
        "data": result
    }

@router.get("/{market_id}")
async def get_competitors_by_market(
    market_id: str,
    category: Optional[str] = None,
    locality: Optional[str] = None,
):
    """Retrieve competitor roster for market ID with explicit data source labeling."""
    cat = category
    if not cat:
        if "coffee" in market_id.lower():
            cat = "Specialty Coffee"
        elif "footwear" in market_id.lower():
            cat = "Footwear"
        elif "fashion" in market_id.lower():
            cat = "Fashion Retail"
        elif "restaurant" in market_id.lower():
            cat = "Restaurant"
        else:
            cat = "Specialty Coffee"

    loc = locality or "Madhapur"
    areas = MarketDataLoader.load_areas()
    match = next((a for a in areas if a["area"].lower() == loc.lower()), None)
    target_lat = match["lat"] if match else 17.4484
    target_lng = match["lng"] if match else 78.3908

    result = await places_service.get_nearby_competitors(
        lat=target_lat,
        lng=target_lng,
        category=cat,
        locality_name=loc
    )
    return {
        "success": True,
        "market_id": market_id,
        "data": result["competitors"],
        "metadata": {
            "data_source": result["data_source"],
            "is_demo_data": result["is_demo_data"],
            "saturation": result["saturation"],
            "competitor_count": result["competitor_count"],
        }
    }
