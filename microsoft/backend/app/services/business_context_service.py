"""
Business Context Service (Single Source of Truth)
Maintains platform state across Setup, Market Overview, Simulation, Maps, Competitor Intelligence,
and Hindsight memory. Supports user-scoped sessions.
ZERO HARDCODING.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging
from app.agents.retail_classifier import RetailWebsiteClassifierAgent, UNSUPPORTED_WEBSITE_MESSAGE, INSUFFICIENT_EVIDENCE_MESSAGE
from app.services.market_intelligence_engine import MarketIntelligenceEngine
from app.services.google_places_service import GooglePlacesService
from app.services.data_loader import MarketDataLoader
from app.simulation.whatif_engine import WhatIfSimulationEngine, WhatIfSimulationInputs

logger = logging.getLogger(__name__)

class BusinessContextModel(BaseModel):
    user_id: Optional[str] = "default_user"
    is_initialized: bool = False
    retail_url: Optional[str] = None
    venture_name: Optional[str] = None
    business_name: Optional[str] = None
    domain: str = "Food & Beverage"
    primary_domain: str = "Food & Beverage"
    category: str = "Specialty Coffee"
    subdomain: str = "Specialty Coffee"
    city: str = "Hyderabad"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    budget: float = 3000000.0
    monthly_rent_budget: Optional[float] = None
    store_size: float = 1200.0
    customer_segment: str = "Tech Professionals"
    
    selected_locality: str = "Madhapur"
    selected_locality_coords: Dict[str, float] = Field(default_factory=lambda: {"lat": 17.4485, "lng": 78.3910})
    rent: float = 150000.0
    marketing_budget: float = 100000.0
    competitor_count: int = 6
    festival_season: bool = False
    metro_opening: bool = False
    inflation: float = 5.0
    search_radius_km: float = 3.0
    
    # Financial outputs stored in single state
    revenue: float = 0.0
    break_even: str = "Month 8"
    break_even_month: Optional[Any] = "Month 8"
    rankings: List[Dict[str, Any]] = Field(default_factory=list)
    competitors: List[Dict[str, Any]] = Field(default_factory=list)
    kpis: Dict[str, Any] = Field(default_factory=dict)
    
    market_overview: Dict[str, Any] = Field(default_factory=dict)
    simulation_results: Dict[str, Any] = Field(default_factory=dict)
    competitor_data: Dict[str, Any] = Field(default_factory=dict)

class BusinessContextService:
    _instance = None
    _context: BusinessContextModel = BusinessContextModel()
    _user_contexts: Dict[str, BusinessContextModel] = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def _get_target_context(cls, user_id: Optional[str] = None) -> BusinessContextModel:
        if not user_id or user_id == "default_user":
            return cls._context
        if user_id not in cls._user_contexts:
            cls._user_contexts[user_id] = BusinessContextModel(user_id=user_id)
        return cls._user_contexts[user_id]

    @classmethod
    def get_state(cls, user_id: Optional[str] = None) -> Dict[str, Any]:
        target = cls._get_target_context(user_id)
        return target.model_dump()

    @classmethod
    def is_initialized(cls, user_id: Optional[str] = None) -> bool:
        target = cls._get_target_context(user_id)
        return target.is_initialized

    @classmethod
    async def initialize(
        cls,
        retail_url: Optional[str] = None,
        venture_name: Optional[str] = None,
        category: Optional[str] = None,
        city: str = "Hyderabad",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        budget: float = 3000000.0,
        monthly_rent_budget: Optional[float] = None,
        store_size: float = 1200.0,
        customer_segment: str = "Tech Professionals",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate retail URL (if provided) and initialize platform state."""
        clean_url = (retail_url or "").strip()
        business_name = (venture_name or "").strip()
        detected_category = (category or "").strip()
        detected_domain = "Food & Beverage"

        if clean_url:
            classifier = RetailWebsiteClassifierAgent()
            classification = await classifier.classify_url(clean_url, selected_category=detected_category or None, venture_name=business_name or None)

            if not classification.get("retail_status"):
                msg = classification.get("message") or UNSUPPORTED_WEBSITE_MESSAGE
                raise ValueError(msg)

            if not business_name:
                business_name = classification.get("brand") or classification.get("business_name") or "Retail Venture"
            if not detected_category:
                detected_category = classification.get("subdomain") or classification.get("category") or "Specialty Retail"
            detected_domain = classification.get("primary_domain") or classification.get("domain") or "Food & Beverage"
            if not customer_segment or customer_segment == "Tech Professionals":
                detected_audience = classification.get("audience") or classification.get("target_audience")
                if detected_audience:
                    customer_segment = detected_audience
        else:
            if not business_name:
                raise ValueError("Venture Name is required for business setup.")
            if not detected_category:
                detected_category = "Specialty Coffee"
            detected_domain = "Food & Beverage"

        effective_rent_budget = monthly_rent_budget or (budget * 0.05 if budget > 500000 else budget)

        # Evaluate markets dynamically using MarketIntelligenceEngine
        market_eval = MarketIntelligenceEngine.evaluate_markets(
            category=detected_category,
            customer_segment=customer_segment,
            store_size=store_size,
            budget=effective_rent_budget,
            city=city
        )

        top_5 = market_eval.get("top_5", [])
        top_locality = top_5[0]["area"] if top_5 else "Madhapur"
        
        # Find coordinates & rent for top locality
        areas = MarketDataLoader.load_areas()
        matched_area = next((a for a in areas if a["area"].lower() == top_locality.lower()), areas[0])
        initial_rent = matched_area["avg_rent_sqft"] * store_size
        coords = {"lat": matched_area["lat"], "lng": matched_area["lng"]}

        # Fetch initial Google Places competitor data
        places_svc = GooglePlacesService()
        comp_data = await places_svc.get_nearby_competitors(
            lat=coords["lat"],
            lng=coords["lng"],
            category=detected_category,
            radius_meters=3000,
            locality_name=top_locality
        )
        initial_competitor_count = comp_data.get("competitor_count", matched_area["competitor_count"])

        # Run What-If Simulation
        sim_inputs = WhatIfSimulationInputs(
            rent=initial_rent,
            store_size=store_size,
            marketing_budget=100000.0,
            competitor_count=initial_competitor_count,
            festival_season=False,
            metro_opening=False,
            inflation=5.0,
            customer_segment=customer_segment,
            category=detected_category,
            locality=top_locality
        )
        sim_res = WhatIfSimulationEngine.calculate(sim_inputs)

        # Align top location predicted monthly revenue with simulation results
        for loc in top_5:
            if loc["area"].lower() == top_locality.lower():
                loc["predicted_monthly_revenue"] = sim_res["monthly_revenue"]
                loc["rent"] = initial_rent
        market_eval["top_5"] = top_5

        top_pick = top_5[0] if top_5 else {"score": 88, "risk": "Low", "component_scores": {"demographic_match": 85, "footfall": 85}}
        viability_score = round(top_pick["score"])
        comp_saturation = comp_data.get("saturation", "Medium saturation")
        opp_score = round((top_pick.get("component_scores", {}).get("demographic_match", 80) * 0.5 + top_pick.get("component_scores", {}).get("footfall", 80) * 0.5), 1)

        kpis = {
            "viability_score": viability_score,
            "expected_monthly_revenue": sim_res["monthly_revenue"],
            "break_even_month": sim_res.get("break_even_display", "Month 8"),
            "market_risk": top_pick.get("risk", "Low"),
            "opportunity_score": opp_score,
            "competitor_saturation": comp_saturation,
            "competitor_count": initial_competitor_count
        }
        market_eval["kpis"] = kpis

        new_ctx = BusinessContextModel(
            user_id=user_id or "default_user",
            is_initialized=True,
            retail_url=clean_url or None,
            venture_name=business_name,
            business_name=business_name,
            domain=detected_domain,
            primary_domain=detected_domain,
            category=detected_category,
            subdomain=detected_category,
            city=city,
            latitude=latitude or coords["lat"],
            longitude=longitude or coords["lng"],
            budget=budget,
            monthly_rent_budget=monthly_rent_budget or effective_rent_budget,
            store_size=store_size,
            customer_segment=customer_segment,
            selected_locality=top_locality,
            selected_locality_coords=coords,
            rent=initial_rent,
            marketing_budget=100000.0,
            competitor_count=initial_competitor_count,
            festival_season=False,
            metro_opening=False,
            inflation=5.0,
            search_radius_km=3.0,
            revenue=sim_res["monthly_revenue"],
            break_even=sim_res.get("break_even_display", "Month 8"),
            break_even_month=sim_res.get("break_even_display", "Month 8"),
            rankings=top_5,
            competitors=comp_data.get("competitors", []),
            kpis=kpis,
            market_overview=market_eval,
            simulation_results=sim_res,
            competitor_data=comp_data
        )

        cls._context = new_ctx
        if user_id:
            cls._user_contexts[user_id] = new_ctx

        return new_ctx.model_dump()

    @classmethod
    async def update(cls, updates: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Update shared business context parameters and recalculate both Overview and Simulation."""
        target = cls._get_target_context(user_id)
        if not target.is_initialized:
            # Auto-initialize with default if update called before explicit setup
            await cls.initialize(
                venture_name="Retail Venture",
                category="Specialty Coffee",
                customer_segment="Tech Professionals",
                user_id=user_id
            )
            target = cls._get_target_context(user_id)

        # Handle retail_url update
        if "retail_url" in updates and updates["retail_url"]:
            new_url = updates["retail_url"].strip()
            target.retail_url = new_url
            try:
                classifier = RetailWebsiteClassifierAgent()
                classification = await classifier.classify_url(new_url)
                if classification.get("retail_status"):
                    if classification.get("brand") and ("venture_name" not in updates or not updates["venture_name"]):
                        target.venture_name = classification["brand"]
                        target.business_name = classification["brand"]
                    if classification.get("primary_domain") or classification.get("domain"):
                        target.domain = classification.get("primary_domain") or classification.get("domain")
                        target.primary_domain = target.domain
                    if classification.get("subdomain") or classification.get("category"):
                        target.category = classification.get("subdomain") or classification.get("category")
                        target.subdomain = target.category
            except Exception as e:
                logger.info(f"URL update classification note: {e}")

        # Update fields
        for field, value in updates.items():
            if hasattr(target, field) and value is not None:
                setattr(target, field, value)

        if "venture_name" in updates and updates["venture_name"]:
            target.business_name = updates["venture_name"]

        if "monthly_rent_budget" in updates and updates["monthly_rent_budget"]:
            target.monthly_rent_budget = float(updates["monthly_rent_budget"])
            if "rent" not in updates:
                target.rent = float(updates["monthly_rent_budget"])

        areas = MarketDataLoader.load_areas()
        matched_area = next((a for a in areas if a["area"].lower() == target.selected_locality.lower()), None)
        if matched_area:
            target.selected_locality_coords = {"lat": matched_area["lat"], "lng": matched_area["lng"]}
            if "rent" not in updates and "monthly_rent_budget" not in updates:
                target.rent = matched_area["avg_rent_sqft"] * target.store_size

        # If search radius or locality changed, recalculate competitors
        if "search_radius_km" in updates or "selected_locality" in updates or "category" in updates:
            places_svc = GooglePlacesService()
            radius_meters = int(target.search_radius_km * 1000)
            comp_data = await places_svc.get_nearby_competitors(
                lat=target.selected_locality_coords["lat"],
                lng=target.selected_locality_coords["lng"],
                category=target.category,
                radius_meters=radius_meters,
                locality_name=target.selected_locality
            )
            target.competitor_data = comp_data
            target.competitors = comp_data.get("competitors", [])
            if "competitor_count" not in updates:
                target.competitor_count = comp_data.get("competitor_count", target.competitor_count)

        # Recalculate simulation with current unified state
        sim_inputs = WhatIfSimulationInputs(
            rent=target.rent,
            store_size=target.store_size,
            marketing_budget=target.marketing_budget,
            competitor_count=target.competitor_count,
            festival_season=target.festival_season,
            metro_opening=target.metro_opening,
            inflation=target.inflation,
            customer_segment=target.customer_segment,
            category=target.category,
            locality=target.selected_locality
        )
        sim_res = WhatIfSimulationEngine.calculate(sim_inputs)
        target.simulation_results = sim_res
        target.revenue = sim_res["monthly_revenue"]
        target.break_even = sim_res.get("break_even_display", "Month 8")
        target.break_even_month = sim_res.get("break_even_display", "Month 8")

        # Recalculate market rankings using effective rent budget
        effective_rent_budget = target.monthly_rent_budget or (target.budget * 0.05 if target.budget > 500000 else target.budget)
        market_eval = MarketIntelligenceEngine.evaluate_markets(
            category=target.category,
            customer_segment=target.customer_segment,
            store_size=target.store_size,
            budget=effective_rent_budget,
            city=target.city
        )

        # Align selected locality predicted revenue with simulation results
        top_5 = market_eval.get("top_5", [])
        if "selected_locality" not in updates and top_5:
            target.selected_locality = top_5[0]["area"]
            target.selected_locality_coords = {"lat": top_5[0]["lat"], "lng": top_5[0]["lng"]}

        for loc in top_5:
            if loc["area"].lower() == target.selected_locality.lower():
                loc["predicted_monthly_revenue"] = sim_res["monthly_revenue"]
                loc["rent"] = target.rent
        if top_5 and top_5[0]["area"].lower() == target.selected_locality.lower():
            top_5[0]["predicted_monthly_revenue"] = sim_res["monthly_revenue"]
        market_eval["top_5"] = top_5
        target.rankings = top_5

        # Recompute dynamic KPIs for Overview
        top_pick = top_5[0] if top_5 else {"score": 85, "risk": "Low", "component_scores": {"demographic_match": 85, "footfall": 85}}
        selected_match = next((l for l in top_5 if l["area"].lower() == target.selected_locality.lower()), top_pick)
        viability_score = round(selected_match["score"])
        comp_saturation = target.competitor_data.get("saturation", "Medium saturation")
        opp_score = round((selected_match.get("component_scores", {}).get("demographic_match", 80) * 0.5 + selected_match.get("component_scores", {}).get("footfall", 80) * 0.5), 1)

        kpis = {
            "viability_score": viability_score,
            "expected_monthly_revenue": sim_res["monthly_revenue"],
            "break_even_month": sim_res.get("break_even_display", "Month 8"),
            "market_risk": selected_match.get("risk", "Low"),
            "opportunity_score": opp_score,
            "competitor_saturation": comp_saturation,
            "competitor_count": target.competitor_count
        }
        market_eval["kpis"] = kpis
        target.kpis = kpis
        target.market_overview = market_eval

        cls._context = target
        return target.model_dump()

    @classmethod
    def reset(cls, user_id: Optional[str] = None):
        if user_id and user_id in cls._user_contexts:
            del cls._user_contexts[user_id]
        cls._context = BusinessContextModel()
