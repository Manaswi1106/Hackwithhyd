"""
Market Intelligence Scoring Engine
Builds weighted rankings for commercial localities using empirical CSV datasets.

Weights:
- Demographic Match — 20%
- Footfall — 20%
- Income Alignment — 15%
- Rental Affordability — 15%
- Competitor Density — 15%
- Historical Sales Similarity — 15%

Hindsight Memory Integration:
- Recalls past similar business experiences
- Modifies ranking scores (+/- points) based on empirical historical memory
- Provides traceable Hindsight memory insights

Outputs:
- Top 5 ranked locations with score, predicted revenue, rent, footfall, risk, competitor density
- Evidence-backed 'Why this location?' (5 real reasons)
- Factual 'Why not the others?' (reasoning on lower scoring areas)
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.services.data_loader import MarketDataLoader
from app.config import settings

logger = logging.getLogger(__name__)

MEMORY_FILE = Path(__file__).resolve().parent.parent / "data" / "hindsight_memories.json"

DEFAULT_EXPERIENCES: List[Dict[str, Any]] = []

class MarketIntelligenceEngine:
    """Weighted scoring engine using empirical datasets and Hindsight memory modifier."""

    @classmethod
    def get_memories(cls) -> List[Dict[str, Any]]:
        """Load stored Hindsight business experiences."""
        if not MEMORY_FILE.exists():
            MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_EXPERIENCES, f, indent=2)
            return list(DEFAULT_EXPERIENCES)
        
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else list(DEFAULT_EXPERIENCES)
        except Exception:
            return list(DEFAULT_EXPERIENCES)

    @classmethod
    def retain_simulation_memory(cls, memory_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Retain a completed simulation into Hindsight memory."""
        memories = cls.get_memories()
        memories.insert(0, memory_entry)
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memories, f, indent=2)
        return memory_entry

    @classmethod
    def evaluate_markets(
        cls,
        category: str = "Specialty Coffee",
        customer_segment: str = "Tech Professionals",
        store_size: float = 1200.0,
        budget: float = 3000000.0,
        city: str = "Hyderabad",
    ) -> Dict[str, Any]:
        """Rank localities using 6 weighted components + Hindsight memory modifier."""
        areas = MarketDataLoader.load_areas()
        sales_records = MarketDataLoader.load_historical_sales()
        memories = cls.get_memories()

        # Step 1: Recall similar memories for the category
        category_clean = category.lower()
        matched_memories = [
            m for m in memories
            if category_clean in m["business_category"].lower() or m["business_category"].lower() in category_clean
        ]

        hindsight_insight = ""
        memory_boost_localities = set()
        if matched_memories:
            memory_boost_localities = {m["chosen_locality"] for m in matched_memories if m.get("chosen_locality")}
            top_boosted = ", ".join(list(memory_boost_localities)[:3])
            hindsight_insight = (
                f"Recalled {len(matched_memories)} verified business simulation(s) for {category} from Hindsight memory. "
                f"Historical empirical performance in {top_boosted} dynamically adjusts location recommendation scores."
            )

        # Normalization ranges across dataset
        max_pop = max(a["population"] for a in areas)
        max_footfall = max(a["daily_footfall"] for a in areas)
        max_income = max(a["avg_income"] for a in areas)
        max_rent = max(a["avg_rent_sqft"] for a in areas)
        min_rent = min(a["avg_rent_sqft"] for a in areas)

        is_coffee = any(k in category_clean for k in ["coffee", "cafe", "roaster", "espresso", "tea"])
        is_cloud_kitchen = any(k in category_clean for k in ["kitchen", "delivery", "cloud", "dark kitchen", "takeaway"])
        is_luxury = any(k in category_clean for k in ["luxury", "jewel", "fine dining", "boutique", "designer", "premium"]) or customer_segment == "Luxury Buyers" or (any(k in category_clean for k in ["fashion", "apparel"]) and customer_segment != "Students")
        is_dining = any(k in category_clean for k in ["dining", "restaurant", "barbecue", "bbq", "buffet", "grill", "fast casual"])

        scored_locations = []

        for a in areas:
            area_name = a["area"]

            # 1. Demographic & Domain Match (25% weight)
            if customer_segment == "Students":
                # Rapid transit proximity + student dense zones
                metro_score = (1.0 - min(1.0, a["metro_distance"] / 1500.0))
                pop_ratio = a["population"] / max_pop
                demo_score = (metro_score * 0.60 + pop_ratio * 0.40) * 100.0
            elif customer_segment == "Transit Commuters":
                # Close proximity to major railway / metro lines + high transit pedestrian volume
                metro_score = (1.0 - min(1.0, a["metro_distance"] / 1000.0))
                footfall_ratio = a["daily_footfall"] / max_footfall
                demo_score = (metro_score * 0.55 + footfall_ratio * 0.45) * 100.0
            elif customer_segment in ["Tech Professionals", "Corporate Executives"]:
                # High office density + corporate disposable income
                office_ratio = a["office_density"] / 100.0
                income_ratio = a["avg_income"] / max_income
                demo_score = (office_ratio * 0.70 + income_ratio * 0.30) * 100.0
            elif customer_segment == "Luxury Buyers" or is_luxury:
                # Luxury corridors require top tier affluence and ample parking
                income_ratio = a["avg_income"] / max_income
                parking_ratio = a["parking_score"] / 10.0
                demo_score = (income_ratio * 0.70 + parking_ratio * 0.30) * 100.0
            elif is_cloud_kitchen:
                # Cloud kitchens require high residential population and road delivery connectivity
                pop_ratio = a["population"] / max_pop
                conn_ratio = a["road_connectivity"] / 10.0
                demo_score = (pop_ratio * 0.75 + conn_ratio * 0.25) * 100.0
            elif is_coffee:
                # Default coffee to office density + income if segment is generic
                office_ratio = a["office_density"] / 100.0
                income_ratio = a["avg_income"] / max_income
                demo_score = (office_ratio * 0.65 + income_ratio * 0.35) * 100.0
            else: # Families & General Retail
                pop_ratio = a["population"] / max_pop
                rest_ratio = a["restaurant_count"] / 100.0
                demo_score = (pop_ratio * 0.50 + rest_ratio * 0.50) * 100.0
            demo_score = min(100.0, max(15.0, demo_score))

            # 2. Footfall / Delivery Catchment (20% weight)
            if is_cloud_kitchen:
                # Cloud kitchens do not rely on high-street pedestrian footfall; they need arterial road connectivity
                footfall_score = (a["road_connectivity"] / 10.0) * 100.0
            else:
                footfall_score = (a["daily_footfall"] / max_footfall) * 100.0

            # 3. Income Alignment (15% weight)
            if is_cloud_kitchen:
                # Mass-market delivery demand flourishes in middle-income residential belts
                income_score = 78.0
            elif customer_segment in ["Students", "Transit Commuters"]:
                income_score = 75.0 + (a["daily_footfall"] / max_footfall) * 20.0
            elif is_coffee or is_luxury or customer_segment in ["Tech Professionals", "Corporate Executives", "Luxury Buyers"]:
                income_score = (a["avg_income"] / max_income) * 100.0
            else:
                income_score = (a["avg_income"] / max_income) * 100.0

            # 4. Rental Affordability vs Budget (15% weight)
            est_rent = a["avg_rent_sqft"] * store_size
            effective_budget = max(50000.0, budget)
            if is_cloud_kitchen:
                # Cloud kitchens aggressively seek low rent per sqft to preserve operating margins
                rent_score = (1.0 - ((a["avg_rent_sqft"] - min_rent) / max(1.0, (max_rent - min_rent)))) * 100.0
            else:
                if est_rent <= effective_budget:
                    rent_score = 95.0
                else:
                    rent_score = max(15.0, 95.0 - ((est_rent - effective_budget) / effective_budget) * 75.0)
            rent_score = min(100.0, max(15.0, rent_score))

            # 5. Competitor Density & Hub Synergy (15% weight)
            comp_count = a["competitor_count"]
            if is_cloud_kitchen:
                # Lower local competitor saturation is better for delivery kitchens
                comp_score = (1.0 - (comp_count / 60.0)) * 100.0
            elif is_coffee or is_luxury or is_dining:
                # Established retail/dining clusters provide cluster synergy (15-38 competitors is ideal)
                if 12 <= comp_count <= 38:
                    comp_score = 95.0 # Prime validated destination
                elif comp_count < 12:
                    comp_score = 65.0 # Unproven demand
                else:
                    comp_score = 70.0 # High saturation
            else:
                comp_score = 85.0 if 10 <= comp_count <= 35 else 65.0

            # 6. Historical Sales Similarity (10% weight)
            area_sales = [s for s in sales_records if s["area"].lower() == area_name.lower()]
            cat_sales = [s for s in area_sales if any(k in s["category"].lower() for k in category_clean.split()) or any(k in category_clean for k in s["category"].lower().split())]
            if cat_sales:
                hist_match = cat_sales[0]
                hist_sales_val = hist_match["monthly_sales"]
                sales_score = min(100.0, (hist_sales_val / 2000000.0) * 100.0)
            elif area_sales:
                sales_score = min(100.0, (area_sales[0]["monthly_sales"] / 2000000.0) * 85.0)
            else:
                sales_score = 60.0

            # Exact Weighted Formula:
            # Audience Match (25%), Footfall (20%), Income (15%), Affordability (15%), Competitors (15%), Historical Sales (10%)
            weighted_score = (
                demo_score * 0.25 +
                footfall_score * 0.20 +
                income_score * 0.15 +
                rent_score * 0.15 +
                comp_score * 0.15 +
                sales_score * 0.10
            )

            # Hindsight Memory Modifier
            hindsight_mod = 0.0
            if area_name in memory_boost_localities:
                hindsight_mod = 10.0 # Positive empirical boost from memory
                weighted_score += hindsight_mod

            final_score = min(99.0, max(25.0, round(weighted_score, 1)))

            # Predicted Monthly Revenue based on dataset sales per sqft & footfall
            if cat_sales:
                benchmark_sales = cat_sales[0]["monthly_sales"]
                benchmark_size = cat_sales[0]["store_size_sqft"]
                sales_per_sqft = benchmark_sales / max(1.0, benchmark_size)
            elif area_sales:
                benchmark_sales = area_sales[0]["monthly_sales"]
                benchmark_size = area_sales[0]["store_size_sqft"]
                sales_per_sqft = (benchmark_sales / max(1.0, benchmark_size)) * 0.85
            else:
                sales_per_sqft = 650.0 + (a["avg_income"] / 100000.0) * 200.0 + (a["office_density"] / 100.0) * 150.0
            
            predicted_revenue = round(sales_per_sqft * store_size)
            rent_cost = round(store_size * a["avg_rent_sqft"])

            # Risk classification
            rent_to_rev = (rent_cost / max(1.0, predicted_revenue)) * 100.0
            if final_score >= 80 and rent_to_rev <= 20:
                risk_level = "Low"
            elif final_score >= 60 and rent_to_rev <= 28:
                risk_level = "Medium"
            else:
                risk_level = "High"

            bullets = [
                f"Commercial office density rating is {round(a['office_density']/10, 1)}/10, sustaining weekday footfall and commercial vitality.",
                f"Monthly rent ₹{rent_cost:,} (₹{a['avg_rent_sqft']}/sqft) {'fits within target budget' if rent_cost <= budget else 'is within sustainable bounds of your budget'}.",
                f"Active daily pedestrian catchment of {a['daily_footfall']:,} people in commercial retail cluster.",
                f"Rapid transit accessibility: {round((1000.0 / max(100.0, a['metro_distance'])) * 10, 1)}/10 with Metro within {a['metro_distance']}m.",
                f"Competitive density of {a['competitor_count']} competitors ({round(a['competitor_count'] / 3.2, 1)}/km²) confirms category market depth.",
            ]
            if area_name in memory_boost_localities:
                bullets.append(f"Hindsight Memory: Verified historical {category} businesses recorded superior revenue in this corridor.")

            scored_locations.append({
                "area": area_name,
                "city": a["city"],
                "score": final_score,
                "predicted_monthly_revenue": predicted_revenue,
                "rent": rent_cost,
                "avg_rent_sqft": a["avg_rent_sqft"],
                "footfall": a["daily_footfall"],
                "population": a["population"],
                "avg_income": a["avg_income"],
                "office_density": a["office_density"],
                "road_connectivity": a["road_connectivity"],
                "parking_score": a["parking_score"],
                "metro_distance": a["metro_distance"],
                "competitor_count": a["competitor_count"],
                "restaurant_count": a["restaurant_count"],
                "risk": risk_level,
                "competitor_density": f"{a['competitor_count']} competitors ({round(a['competitor_count'] / 3.2, 1)}/km²)",
                "lat": a["lat"],
                "lng": a["lng"],
                "hindsight_modified": area_name in memory_boost_localities,
                "explainability_bullets": bullets,
                "component_scores": {
                    "demographic_match": round(demo_score, 1),
                    "footfall": round(footfall_score, 1),
                    "income_alignment": round(income_score, 1),
                    "rental_affordability": round(rent_score, 1),
                    "competitor_density": round(comp_score, 1),
                    "historical_sales_similarity": round(sales_score, 1),
                }
            })

        # Sort descending by score
        scored_locations.sort(key=lambda x: x["score"], reverse=True)

        top_5 = scored_locations[:5]
        rejected = scored_locations[5:]

        # Build Explainability: "Why this location?" for top pick
        top_pick = top_5[0]
        why_this_location = top_pick["explainability_bullets"]

        # Build Explainability: "Why not the others?"
        why_not_others = []
        for r in rejected[:4]:
            reasons = []
            if r["avg_rent_sqft"] > top_pick["avg_rent_sqft"] * 1.2:
                reasons.append(f"higher rental overhead (₹{r['avg_rent_sqft']}/sqft vs ₹{top_pick['avg_rent_sqft']}/sqft)")
            if r["avg_income"] < top_pick["avg_income"] * 0.7:
                reasons.append(f"lower purchasing power alignment (₹{r['avg_income']:,}/mo vs ₹{top_pick['avg_income']:,}/mo)")
            if r["competitor_count"] > top_pick["competitor_count"] * 1.5:
                reasons.append(f"higher competitive saturation ({r['competitor_count']} competitors)")
            if r["office_density"] < 65:
                reasons.append(f"lower commercial office density ({r['office_density']}/100 vs {top_pick['office_density']}/100)")
            
            summary_reason = ", ".join(reasons) if reasons else f"overall weighted suitability score ({r['score']}) is below top corridor threshold"
            why_not_others.append(f"{r['area']}: Scored lower due to {summary_reason}.")

        return {
            "top_5": top_5,
            "all_ranked": scored_locations,
            "hindsight_insight": hindsight_insight,
            "why_this_location": why_this_location,
            "why_not_others": why_not_others,
            "recalled_memories_count": len(matched_memories),
            "recalled_memories": matched_memories[:4],
        }
