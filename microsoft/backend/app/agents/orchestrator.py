"""
VentureScope Orchestrator Agent
Coordinates the complete end-to-end intelligence and simulation workflow:

USER INPUT
    ↓
ORCHESTRATOR
    ↓
MARKET AGENT ─── COMPETITOR AGENT ─── CUSTOMER AGENT ─── VENTURE AGENT (if URL)
    ↓
EVIDENCE VERIFICATION & AUDIT
    ↓
HINDSIGHT MEMORY (Recall previous → Retain new → Compare "What Changed?")
    ↓
GAP ANALYSIS
    ↓
DETERMINISTIC TRAJECTORY ENGINE & SIMULATION ENGINE
    ↓
EXPLANATION GENERATION
    ↓
COMPLETE DASHBOARD INTELLIGENCE
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

from app.agents.market_agent import MarketResearchAgent
from app.agents.competitor_agent import CompetitorResearchAgent
from app.agents.customer_agent import CustomerIntelligenceAgent
from app.agents.venture_agent import VentureAnalysisAgent
from app.agents.evidence_agent import EvidenceVerificationAgent
from app.agents.opportunity_agent import OpportunityAgent
from app.agents.simulation_agent import SimulationAssumptionAgent
from app.agents.explanation_agent import ExplanationAgent
from app.trajectory.engine import TrajectoryEngine, TrajectoryAssumptions
from app.hindsight.memory_service import HindsightMemoryService
from app.hindsight.providers import create_hindsight_provider
from app.config import settings

logger = logging.getLogger(__name__)


class VentureScopeOrchestrator:
    """Master orchestrator for the venture intelligence and simulation pipeline."""

    def __init__(self, hindsight_service: Optional[HindsightMemoryService] = None):
        self.market_agent = MarketResearchAgent()
        self.competitor_agent = CompetitorResearchAgent()
        self.customer_agent = CustomerIntelligenceAgent()
        self.venture_agent = VentureAnalysisAgent()
        self.evidence_agent = EvidenceVerificationAgent()
        self.opportunity_agent = OpportunityAgent()
        self.simulation_agent = SimulationAssumptionAgent()
        self.explanation_agent = ExplanationAgent()

        if hindsight_service:
            self.hindsight = hindsight_service
        else:
            provider = create_hindsight_provider(
                api_token=settings.hindsight_api_token,
                base_url=settings.hindsight_api_url,
            )
            self.hindsight = HindsightMemoryService(
                provider=provider,
                bank_id=settings.hindsight_bank_id,
            )

    async def run_full_pipeline(
        self,
        city: str = "Hyderabad",
        category: str = "Fashion & Lifestyle",
        subcategory: str = "Footwear",
        venture_url: Optional[str] = None,
        venture_name: Optional[str] = None,
        deployment_model: str = "hybrid",
        target_location: str = "Gachibowli",
        what_if_overrides: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Execute the coordinated intelligence workflow."""
        market_id = f"{city}_{category}_{subcategory}".lower().replace(" ", "_")

        # 1. Parallel research execution
        market_data = await self.market_agent.analyze_market(city, category, subcategory)
        competitors = await self.competitor_agent.discover_competitors(category, subcategory, city)
        customer_intel = await self.customer_agent.analyze_customer_demand(category, subcategory)
        gaps = await self.opportunity_agent.analyze_gaps(category, subcategory, city)

        # 2. Venture X-Ray (if URL provided or venture specified)
        venture_analysis = await self.venture_agent.analyze_venture(
            venture_url=venture_url,
            venture_name=venture_name,
            category=category,
            subcategory=subcategory,
        )

        # 3. Deterministic Trajectory Calculation
        traj_engine = TrajectoryEngine(TrajectoryAssumptions())
        trajectory_scenarios = traj_engine.generate_all_scenarios(months=24)
        trajectory_explanation = self.explanation_agent.explain_trajectory(trajectory_scenarios)

        # 4. Deterministic Financial Simulation
        sim_assumptions = self.simulation_agent.prepare_assumptions(
            market_data=market_data,
            venture_data=venture_analysis,
            deployment_model=deployment_model,
            target_location=target_location,
            custom_overrides=what_if_overrides,
        )
        sim_results = self.simulation_agent.execute_simulation(sim_assumptions, months=24)
        sim_explanations = self.explanation_agent.explain_simulation(sim_results, sim_assumptions)

        # 5. HINDSIGHT MEMORY LAYER (Central Demo Loop)
        current_market_state = {
            "city": city,
            "category": category,
            "subcategory": subcategory,
            "competitor_count": len(competitors),
            "average_price": market_data["pulse"]["average_price"]["value"],
            "demand_signal": market_data["pulse"]["demand_trend"]["value"],
            "top_locations": [loc["name"] for loc in market_data["top_locations"][:4]],
            "customer_segments": [s["name"] for s in customer_intel["segments"][:3]],
        }

        # Compare with previous analysis from Hindsight memory
        hindsight_comparison = await self.hindsight.compare_with_previous(
            market_id=market_id,
            current_state=current_market_state,
        )

        # Retain new snapshot into Hindsight for future comparisons
        memory_id = await self.hindsight.remember_market_state(
            market_id=market_id,
            state=current_market_state,
        )

        # If a venture is analyzed, retain venture intelligence too
        venture_memory_id = None
        if venture_name or venture_url:
            v_id = venture_name or "venture_01"
            venture_memory_id = await self.hindsight.remember_venture_analysis(
                venture_id=v_id,
                analysis={
                    "name": venture_analysis["name"],
                    "url": venture_analysis["url"],
                    "business_model": venture_analysis["xray"]["business_model"]["value"],
                    "price": venture_analysis["xray"]["price"]["value"],
                    "positioning": venture_analysis["xray"]["positioning"]["value"],
                    "target_audience": venture_analysis["xray"]["target_audience"]["value"],
                    "differentiators": venture_analysis["xray"]["differentiators"],
                    "competitive_overlap": venture_analysis["xray"]["competitive_overlap"],
                    "strengths": venture_analysis["xray"]["strength_signals"],
                    "risks": venture_analysis["xray"]["risk_signals"],
                }
            )

        return {
            "market_id": market_id,
            "city": city,
            "category": category,
            "subcategory": subcategory,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "market_overview": {
                "pulse": market_data["pulse"],
                "locations": market_data["top_locations"],
                "trajectory": {
                    "scenarios": trajectory_scenarios,
                    "explanation": trajectory_explanation,
                },
            },
            "competitors": competitors,
            "customer_intelligence": customer_intel,
            "venture_xray": venture_analysis,
            "simulation": {
                "assumptions": {
                    "deployment_model": sim_assumptions.deployment_model,
                    "target_location": sim_assumptions.target_location,
                    "monthly_customers": sim_assumptions.monthly_customers_base,
                    "cac": sim_assumptions.customer_acquisition_cost,
                    "aov": sim_assumptions.average_order_value,
                    "retention_rate": sim_assumptions.retention_rate,
                    "operating_cost_monthly": sim_assumptions.operating_cost_monthly,
                    "marketing_budget_monthly": sim_assumptions.marketing_budget_monthly,
                    "gross_margin_percent": sim_assumptions.gross_margin_percent,
                    "investment_amount": sim_assumptions.investment_amount,
                },
                "results": sim_results,
                "explanations": sim_explanations,
            },
            "market_gaps": gaps,
            "hindsight": {
                "memory_id": memory_id,
                "venture_memory_id": venture_memory_id,
                "comparison": hindsight_comparison,
            }
        }
