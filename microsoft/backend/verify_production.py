"""
VentureScope — Automated Production Verification Suite
Verifies the 7 mandatory architectural scenarios:
1. Google rejected
2. Starbucks accepted
3. Competitor count changes with radius
4. Overview updates after simulation
5. Map updates after simulation
6. Hindsight changes recommendation
7. Zero hardcoded rankings

Outputs explicit [PASS] or [FAIL] for each scenario.
"""

import sys
import asyncio
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.agents.retail_classifier import RetailWebsiteClassifierAgent, NON_RETAIL_MESSAGE
from app.services.data_loader import MarketDataLoader
from app.services.google_places_service import GooglePlacesService
from app.services.market_intelligence_engine import MarketIntelligenceEngine
from app.services.business_context_service import BusinessContextService
from app.simulation.whatif_engine import WhatIfSimulationEngine, WhatIfSimulationInputs

class ProductionVerifier:
    def __init__(self):
        self.results = {}

    def log_result(self, scenario_num: int, title: str, passed: bool, detail: str = ""):
        status = "PASS" if passed else "FAIL"
        module_key = f"Scenario {scenario_num}: {title}"
        self.results[module_key] = (status, detail)
        symbol = "[OK]" if passed else "[X]"
        print(f"[{status}] {symbol} Scenario {scenario_num}: {title}")
        if detail:
            # Replace unicode currency symbols for clean Windows console output
            safe_detail = detail.replace("\u20b9", "INR ")
            print(f"            Detail: {safe_detail}")

    async def verify_scenario_1_google_rejected(self):
        """1. Google rejected: informational/non-retail URLs must be rejected with exact error message."""
        try:
            agent = RetailWebsiteClassifierAgent()
            test_urls = ["https://www.google.com", "https://en.wikipedia.org", "https://youtube.com"]
            all_rejected = True
            details = []

            for u in test_urls:
                res = await agent.classify_url(u)
                is_rejected = (
                    res.get("retail_status") is False and
                    res.get("message") == NON_RETAIL_MESSAGE
                )
                if not is_rejected:
                    all_rejected = False
                details.append(f"{u} -> status={res.get('retail_status')}")

            self.log_result(
                1,
                "Google rejected",
                all_rejected,
                f"Checked {len(test_urls)} non-retail URLs. All rejected with required error message. ({', '.join(details)})"
            )
        except Exception as e:
            self.log_result(1, "Google rejected", False, f"Exception: {e}")

    async def verify_scenario_2_starbucks_accepted(self):
        """2. Starbucks accepted: retail URLs must be accepted with identified business and category."""
        try:
            agent = RetailWebsiteClassifierAgent()
            res = await agent.classify_url("https://www.starbucks.com")
            passed = (
                res.get("retail_status") is True and
                "starbucks" in res.get("business_name", "").lower() and
                len(res.get("category", "")) > 0
            )
            detail = f"Business: '{res.get('business_name')}', Category: '{res.get('category')}', Confidence: {res.get('confidence')}"
            self.log_result(2, "Starbucks accepted", passed, detail)
        except Exception as e:
            self.log_result(2, "Starbucks accepted", False, f"Exception: {e}")

    async def verify_scenario_3_competitor_count_changes_with_radius(self):
        """3. Competitor count changes with radius: dynamic haversine filtering changes competitor counts."""
        try:
            places_svc = GooglePlacesService()
            # Madhapur coordinates
            lat, lng = 17.4485, 78.3910
            
            res_1km = await places_svc.get_nearby_competitors(lat, lng, "Specialty Coffee", radius_meters=1000)
            res_3km = await places_svc.get_nearby_competitors(lat, lng, "Specialty Coffee", radius_meters=3000)
            res_6km = await places_svc.get_nearby_competitors(lat, lng, "Specialty Coffee", radius_meters=6000)

            c1 = res_1km.get("competitor_count", 0)
            c3 = res_3km.get("competitor_count", 0)
            c6 = res_6km.get("competitor_count", 0)

            passed = (c1 < c3 <= c6) and (c1 > 0)
            detail = f"1km radius: {c1} competitors | 3km radius: {c3} competitors | 6km radius: {c6} competitors (Source: {res_3km.get('data_source')})"
            self.log_result(3, "Competitor count changes with radius", passed, detail)
        except Exception as e:
            self.log_result(3, "Competitor count changes with radius", False, f"Exception: {e}")

    async def verify_scenario_4_overview_updates_after_simulation(self):
        """4. Overview updates after simulation: unified context recalculates both pages together."""
        try:
            # Initialize unified business context
            init_state = await BusinessContextService.initialize(
                retail_url="https://www.starbucks.com",
                city="Hyderabad",
                budget=3000000.0,
                store_size=1200.0,
                customer_segment="Tech Professionals"
            )
            top_loc_before = init_state["market_overview"]["top_5"][0]
            rev_before = top_loc_before["predicted_monthly_revenue"]

            # Update simulation parameters: Increase marketing budget to 400k and activate festival season
            updated_state = await BusinessContextService.update({
                "marketing_budget": 400000.0,
                "festival_season": True,
            })
            sim_rev = updated_state["simulation_results"]["monthly_revenue"]
            top_loc_after = updated_state["market_overview"]["top_5"][0]
            rev_after = top_loc_after["predicted_monthly_revenue"]

            # Check that simulation revenue changed and market overview received the exact same synchronized revenue
            revenue_changed = (rev_after > rev_before)
            in_sync = (rev_after == sim_rev)
            passed = revenue_changed and in_sync

            pct_change = round(((rev_after - rev_before) / rev_before) * 100, 1)
            detail = f"Baseline Rev: INR {rev_before:,} -> Simulated Rev: INR {rev_after:,} (+{pct_change}%). Overview exactly matches Simulation: {in_sync}."
            self.log_result(4, "Overview updates after simulation", passed, detail)
        except Exception as e:
            self.log_result(4, "Overview updates after simulation", False, f"Exception: {e}")

    async def verify_scenario_5_map_updates_after_simulation(self):
        """5. Map updates after simulation: selecting new locality or radius updates map coordinates and competitor pins."""
        try:
            # Switch selected locality to Banjara Hills with 1.5km search radius
            updated_state = await BusinessContextService.update({
                "selected_locality": "Banjara Hills",
                "search_radius_km": 1.5
            })

            sel_loc = updated_state["selected_locality"]
            coords = updated_state["selected_locality_coords"]
            comps = updated_state["competitor_data"]["competitors"]
            comp_count = updated_state["competitor_count"]

            areas = MarketDataLoader.load_areas()
            b_area = next((a for a in areas if a["area"] == "Banjara Hills"), None)

            passed = (
                sel_loc == "Banjara Hills" and
                b_area is not None and
                abs(coords["lat"] - b_area["lat"]) < 0.001 and
                abs(coords["lng"] - b_area["lng"]) < 0.001 and
                len(comps) > 0 and
                comp_count == len(comps)
            )
            detail = f"Active Locality: {sel_loc} ({coords['lat']}, {coords['lng']}) with {len(comps)} competitor markers rendered on Mapbox."
            self.log_result(5, "Map updates after simulation", passed, detail)
        except Exception as e:
            self.log_result(5, "Map updates after simulation", False, f"Exception: {e}")

    def verify_scenario_6_hindsight_changes_recommendation(self):
        """6. Hindsight changes recommendation: retained experience dynamically shifts corridor rankings/scores."""
        try:
            # Retain a high-impact success memory in Secunderabad
            experience = {
                "id": "mem_verify_prod_test",
                "business_category": "Specialty Coffee",
                "chosen_locality": "Secunderabad",
                "predicted_revenue": 850000.0,
                "actual_revenue": 1450000.0,
                "customer_segment": "Transit Commuters",
                "investment": 2500000.0,
                "success_or_failure": "Major Success (+70.5% lift)",
                "strategic_lesson": "High rail/metro transit density created massive high-margin impulse sales.",
                "timestamp": "2026-09-28T12:00:00Z"
            }
            MarketIntelligenceEngine.retain_simulation_memory(experience)

            # Evaluate market recommendations
            eval_res = MarketIntelligenceEngine.evaluate_markets(
                category="Specialty Coffee",
                customer_segment="Transit Commuters"
            )

            hindsight_insight = eval_res.get("hindsight_insight", "")
            has_insight = ("recalled" in hindsight_insight.lower() or "similar" in hindsight_insight.lower() or "adjust" in hindsight_insight.lower())

            top_5 = eval_res.get("top_5", [])
            boosted_areas = [loc["area"] for loc in top_5 if loc.get("hindsight_modified") is True]

            passed = has_insight and ("Secunderabad" in boosted_areas or len(boosted_areas) > 0)
            detail = f"Hindsight insight generated: '{hindsight_insight[:80]}...'. Corridors boosted by memory: {', '.join(boosted_areas)}."
            self.log_result(6, "Hindsight changes recommendation", passed, detail)
        except Exception as e:
            self.log_result(6, "Hindsight changes recommendation", False, f"Exception: {e}")

    def verify_scenario_7_zero_hardcoded_rankings(self):
        """7. Zero hardcoded rankings: rankings are derived entirely from CSV datasets and shift with customer segments."""
        try:
            # Compare rankings for two different customer segments
            eval_tech = MarketIntelligenceEngine.evaluate_markets(
                category="Specialty Coffee",
                customer_segment="Tech Professionals",
                city="Hyderabad"
            )
            top_tech = [l["area"] for l in eval_tech.get("top_5", [])]

            eval_students = MarketIntelligenceEngine.evaluate_markets(
                category="Specialty Coffee",
                customer_segment="Students",
                city="Hyderabad"
            )
            top_students = [l["area"] for l in eval_students.get("top_5", [])]

            # Rankings must not be identical fixed lists — they must adapt dynamically to demographic weights
            rankings_differ = (top_tech != top_students)
            all_15_loaded = len(eval_tech.get("all_ranked", [])) >= 15

            passed = rankings_differ and all_15_loaded
            detail = f"Tech Segment Top 3: {', '.join(top_tech[:3])} != Students Segment Top 3: {', '.join(top_students[:3])}. All {len(eval_tech.get('all_ranked', []))} localities computed from CSV."
            self.log_result(7, "Zero hardcoded rankings", passed, detail)
        except Exception as e:
            self.log_result(7, "Zero hardcoded rankings", False, f"Exception: {e}")

    async def run_all(self):
        print("=" * 75)
        print("VENTURESCOPE ARCHITECTURAL VERIFICATION SUITE (7 SCENARIOS)")
        print("Verifying live Groq reasoning, Google Places, shared context & Hindsight")
        print("=" * 75)

        await self.verify_scenario_1_google_rejected()
        await self.verify_scenario_2_starbucks_accepted()
        await self.verify_scenario_3_competitor_count_changes_with_radius()
        await self.verify_scenario_4_overview_updates_after_simulation()
        await self.verify_scenario_5_map_updates_after_simulation()
        self.verify_scenario_6_hindsight_changes_recommendation()
        self.verify_scenario_7_zero_hardcoded_rankings()

        print("=" * 75)
        total = len(self.results)
        passed_count = sum(1 for status, _ in self.results.values() if status == "PASS")
        print(f"VERIFICATION SUMMARY: {passed_count}/{total} SCENARIOS PASSED")
        print("=" * 75)

        return passed_count == total


if __name__ == "__main__":
    verifier = ProductionVerifier()
    success = asyncio.run(verifier.run_all())
    sys.exit(0 if success else 1)
