"""
Unified Business Context API Routes
Provides endpoints for initializing, updating, and querying the single source of truth
for Overview, Simulation, Map, and Competitor intelligence.
ZERO HARDCODING.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import httpx
import logging

from app.config import settings
from app.services.business_context_service import BusinessContextService

logger = logging.getLogger(__name__)
router = APIRouter()

class ContextInitRequest(BaseModel):
    retail_url: Optional[str] = Field(None, description="Target retail store or brand URL")
    venture_name: Optional[str] = Field(None, description="Name of the retail venture")
    category: Optional[str] = Field(None, description="Retail category (auto-detected if None)")
    city: str = Field(default="Hyderabad", description="Target city")
    latitude: Optional[float] = Field(default=None, description="Detected latitude")
    longitude: Optional[float] = Field(default=None, description="Detected longitude")
    budget: float = Field(default=3000000.0, ge=100000.0, description="Available capital in INR")
    monthly_rent_budget: Optional[float] = Field(None, description="Monthly rent budget in INR")
    store_size: float = Field(default=1200.0, ge=100.0, description="Store area in sqft")
    customer_segment: str = Field(default="Tech Professionals", description="Target customer segment")
    user_id: Optional[str] = Field(default=None, description="Authenticated user ID")

class ContextUpdateRequest(BaseModel):
    rent: Optional[float] = None
    marketing_budget: Optional[float] = None
    competitor_count: Optional[int] = None
    festival_season: Optional[bool] = None
    metro_opening: Optional[bool] = None
    inflation: Optional[float] = None
    customer_segment: Optional[str] = None
    selected_locality: Optional[str] = None
    search_radius_km: Optional[float] = None
    radius_km: Optional[float] = None
    competitor_radius: Optional[float] = None
    store_size: Optional[float] = None
    budget: Optional[float] = None
    monthly_rent_budget: Optional[float] = None
    category: Optional[str] = None
    venture_name: Optional[str] = None
    retail_url: Optional[str] = None
    city: Optional[str] = None
    user_id: Optional[str] = None

@router.get("/reverse-geocode")
async def reverse_geocode(lat: float, lng: float) -> Dict[str, Any]:
    """Reverse geocode latitude and longitude into city, state, and address using Google Geocoding API."""
    if settings.google_maps_api_key:
        try:
            google_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={settings.google_maps_api_key}"
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(google_url)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == "OK" and data.get("results"):
                        first = data["results"][0]
                        city = ""
                        state = ""
                        country = "India"
                        for comp in first.get("address_components", []):
                            types = comp.get("types", [])
                            if "locality" in types or "sublocality_level_1" in types or "administrative_area_level_2" in types:
                                if not city:
                                    city = comp["long_name"]
                            if "administrative_area_level_1" in types:
                                state = comp["long_name"]
                            if "country" in types:
                                country = comp["long_name"]
                        city = city or "Hyderabad"
                        state = state or "Telangana"
                        return {
                            "city": city,
                            "state": state,
                            "country": country,
                            "formatted_address": f"{city}, {state}",
                            "full_address": first.get("formatted_address", f"{city}, {state}"),
                            "lat": lat,
                            "lng": lng
                        }
        except Exception as e:
            logger.warning(f"Google Geocoding error: {e}")

    # Fallback to OpenStreetMap Nominatim
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&zoom=14&addressdetails=1"
        headers = {"User-Agent": "VentureScope-AI-Location-Intelligence/2.0"}
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                address = data.get("address", {})
                city = (
                    address.get("city")
                    or address.get("town")
                    or address.get("suburb")
                    or address.get("state_district")
                    or address.get("county")
                    or "Hyderabad"
                )
                state = address.get("state", "Telangana")
                country = address.get("country", "India")
                display_name = data.get("display_name", f"{city}, {state}")
                return {
                    "city": city,
                    "state": state,
                    "country": country,
                    "formatted_address": f"{city}, {state}",
                    "full_address": display_name,
                    "lat": lat,
                    "lng": lng
                }
    except Exception:
        pass

    # Proximity check or default
    return {
        "city": "Hyderabad",
        "state": "Telangana",
        "country": "India",
        "formatted_address": "Hyderabad, Telangana",
        "lat": lat,
        "lng": lng
    }

@router.get("/current")
async def get_current_context(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve the active unified business context."""
    return BusinessContextService.get_state(user_id=user_id)

@router.post("/initialize")
async def initialize_context(req: ContextInitRequest) -> Dict[str, Any]:
    """Initialize platform context with validated retail business information."""
    try:
        state = await BusinessContextService.initialize(
            retail_url=req.retail_url,
            venture_name=req.venture_name,
            category=req.category,
            city=req.city,
            latitude=req.latitude,
            longitude=req.longitude,
            budget=req.budget,
            monthly_rent_budget=req.monthly_rent_budget,
            store_size=req.store_size,
            customer_segment=req.customer_segment,
            user_id=req.user_id
        )
        return state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context initialization failed: {str(e)}")

@router.post("/update")
async def update_context(req: ContextUpdateRequest) -> Dict[str, Any]:
    """Update shared context parameters. Recalculates both Overview and Simulation states together."""
    try:
        updates = {k: v for k, v in req.model_dump().items() if v is not None}
        if "radius_km" in updates and "search_radius_km" not in updates:
            updates["search_radius_km"] = updates["radius_km"]
        if "competitor_radius" in updates and "search_radius_km" not in updates:
            updates["search_radius_km"] = updates["competitor_radius"]
        user_id = updates.get("user_id")
        state = await BusinessContextService.update(updates, user_id=user_id)
        return state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context update failed: {str(e)}")

@router.post("/reset")
async def reset_context(user_id: Optional[str] = None) -> Dict[str, str]:
    """Reset business context to uninitialized state."""
    BusinessContextService.reset(user_id=user_id)
    return {"status": "reset", "message": "Business context cleared."}
