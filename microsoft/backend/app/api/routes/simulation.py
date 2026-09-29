"""
Simulation API Routes
Comprehensive endpoints for:
- 500-person calibrated synthetic market simulation (domain-agnostic)
- 24-month deterministic financial projections
- 10,000-run Monte Carlo stochastic risk modeling
- Stress testing under competitive/macroeconomic shocks
- 2D Decision surface mapping (Price vs Budget)
- Investor Exposure evaluation (Strengths, Risks, Unknowns)
- "Test this change" Recommendation Intervention testing
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from app.simulation.engine import SimulationAssumptions, VentureSimulationEngine
from app.simulation.synthetic_market import SyntheticMarketEngine
from app.simulation.dynamic_population import DynamicPopulationGenerator
from app.simulation.monte_carlo import MonteCarloEngine, MonteCarloParams
from app.simulation.scenarios import StressTestEngine, DecisionSurfaceEngine, InvestorExposureEngine
from app.simulation.whatif_engine import WhatIfSimulationEngine, WhatIfSimulationInputs
from app.agents.explanation_agent import ExplanationAgent
from app.agents.recommendation_engine import RecommendationEngine

router = APIRouter()
explanation_agent = ExplanationAgent()
recommendation_engine = RecommendationEngine()


class RunSimulationRequest(BaseModel):
    deployment_model: str = "hybrid"
    monthly_customers: int = 500
    customer_acquisition_cost: float = 300.0
    average_order_value: float = 3500.0
    purchase_frequency: float = 1.5
    retention_rate: float = 0.40
    operating_cost_monthly: float = 250000.0
    marketing_budget_monthly: float = 150000.0
    gross_margin_percent: float = 0.55
    investment_amount: float = 3000000.0
    target_location: Optional[str] = "Gachibowli"


class DeploySimulationRequest(BaseModel):
    venture_price: float = 3499.0
    market_median_price: float = 2100.0
    marketing_budget: float = 150000.0
    random_seed: int = 42
    domain: Optional[str] = None
    sub_domain: Optional[str] = None


class MonteCarloRequest(BaseModel):
    monthly_customers: int = 500
    customer_acquisition_cost: float = 300.0
    average_order_value: float = 3500.0
    purchase_frequency: float = 1.5
    retention_rate: float = 0.40
    operating_cost_monthly: float = 250000.0
    marketing_budget_monthly: float = 150000.0
    gross_margin_percent: float = 0.55
    investment_amount: float = 3000000.0
    runs: int = 10000


class StressTestRequest(BaseModel):
    base_assumptions: Optional[RunSimulationRequest] = None
    custom_deltas: Optional[Dict[str, float]] = None


class WhatIfRequest(BaseModel):
    simulation_id: Optional[str] = "sim_current"
    changes: Dict[str, float]


class TestInterventionRequest(BaseModel):
    recommendation: Dict[str, Any]
    current_assumptions: Optional[Dict[str, float]] = None
    months: int = 24


@router.post("/run")
async def run_simulation(payload: RunSimulationRequest):
    """Execute a 24-month deterministic simulation across Optimistic, Expected, and Pessimistic scenarios."""
    assumptions = SimulationAssumptions(
        deployment_model=payload.deployment_model,
        monthly_customers_base=payload.monthly_customers,
        customer_acquisition_cost=payload.customer_acquisition_cost,
        average_order_value=payload.average_order_value,
        purchase_frequency=payload.purchase_frequency,
        retention_rate=payload.retention_rate,
        operating_cost_monthly=payload.operating_cost_monthly,
        marketing_budget_monthly=payload.marketing_budget_monthly,
        gross_margin_percent=payload.gross_margin_percent,
        investment_amount=payload.investment_amount,
        target_location=payload.target_location,
    )

    engine = VentureSimulationEngine(assumptions)
    results = engine.run_all_scenarios(months=24)
    explanations = explanation_agent.explain_simulation(results, assumptions)

    return {
        "success": True,
        "assumptions": payload.model_dump(),
        "results": results,
        "explanations": explanations,
    }


@router.post("/deploy")
async def deploy_synthetic_market(payload: DeploySimulationRequest):
    """Simulate 500 calibrated synthetic market participants against venture profile.
    Dynamically generates population based on detected domain."""
    if payload.domain and payload.domain not in ("footwear", "fashion-lifestyle"):
        generator = DynamicPopulationGenerator(random_seed=payload.random_seed)
        market_result = generator.generate(
            domain=payload.domain,
            sub_domain=payload.sub_domain or "",
            venture_price=payload.venture_price,
            market_median_price=payload.market_median_price,
            marketing_budget=payload.marketing_budget,
        )
    else:
        # Calibrated Hyderabad market engine
        engine = SyntheticMarketEngine(random_seed=payload.random_seed)
        market_result = engine.generate_population(
            venture_price=payload.venture_price,
            market_median_price=payload.market_median_price,
            marketing_budget=payload.marketing_budget,
        )

    return {
        "success": True,
        "data": market_result,
    }


@router.post("/monte-carlo")
async def run_monte_carlo(payload: MonteCarloRequest):
    """Execute ~10,000 stochastic trial simulations to calculate percentiles and probability distributions."""
    params = MonteCarloParams(
        monthly_customers_base=payload.monthly_customers,
        customer_acquisition_cost=payload.customer_acquisition_cost,
        average_order_value=payload.average_order_value,
        purchase_frequency=payload.purchase_frequency,
        retention_rate=payload.retention_rate,
        operating_cost_monthly=payload.operating_cost_monthly,
        marketing_budget_monthly=payload.marketing_budget_monthly,
        gross_margin_percent=payload.gross_margin_percent,
        investment_amount=payload.investment_amount,
        runs=payload.runs,
    )
    engine = MonteCarloEngine(params)
    results = engine.run()
    return {
        "success": True,
        "data": results,
    }


@router.post("/stress-test")
async def run_stress_test(payload: StressTestRequest):
    """Stress test venture performance under systematic shocks."""
    p = payload.base_assumptions or RunSimulationRequest()
    base_assumptions = SimulationAssumptions(
        deployment_model=p.deployment_model,
        monthly_customers_base=p.monthly_customers,
        customer_acquisition_cost=p.customer_acquisition_cost,
        average_order_value=p.average_order_value,
        purchase_frequency=p.purchase_frequency,
        retention_rate=p.retention_rate,
        operating_cost_monthly=p.operating_cost_monthly,
        marketing_budget_monthly=p.marketing_budget_monthly,
        gross_margin_percent=p.gross_margin_percent,
        investment_amount=p.investment_amount,
        target_location=p.target_location,
    )
    stress_results = StressTestEngine.evaluate_stress_test(
        base_assumptions=base_assumptions,
        custom_shocks=payload.custom_deltas,
    )
    return {
        "success": True,
        "data": stress_results,
    }


@router.post("/decision-surface")
async def get_decision_surface(payload: Optional[RunSimulationRequest] = None):
    """Generate 2D Decision Surface (Price vs Marketing Budget)."""
    p = payload or RunSimulationRequest()
    base_assumptions = SimulationAssumptions(
        deployment_model=p.deployment_model,
        monthly_customers_base=p.monthly_customers,
        customer_acquisition_cost=p.customer_acquisition_cost,
        average_order_value=p.average_order_value,
        purchase_frequency=p.purchase_frequency,
        retention_rate=p.retention_rate,
        operating_cost_monthly=p.operating_cost_monthly,
        marketing_budget_monthly=p.marketing_budget_monthly,
        gross_margin_percent=p.gross_margin_percent,
        investment_amount=p.investment_amount,
    )
    surface = DecisionSurfaceEngine.generate_surface(base_assumptions=base_assumptions)
    return {
        "success": True,
        "data": surface,
    }


@router.post("/investor-exposure")
async def get_investor_exposure(payload: Optional[RunSimulationRequest] = None):
    """Generate structured balance sheet of Strengths, Risks, and Unknowns."""
    p = payload or RunSimulationRequest()
    base_assumptions = SimulationAssumptions(
        deployment_model=p.deployment_model,
        monthly_customers_base=p.monthly_customers,
        customer_acquisition_cost=p.customer_acquisition_cost,
        average_order_value=p.average_order_value,
        purchase_frequency=p.purchase_frequency,
        retention_rate=p.retention_rate,
        operating_cost_monthly=p.operating_cost_monthly,
        marketing_budget_monthly=p.marketing_budget_monthly,
        gross_margin_percent=p.gross_margin_percent,
        investment_amount=p.investment_amount,
    )
    # Run quick Monte Carlo for risk metrics
    mc_engine = MonteCarloEngine(MonteCarloParams(runs=2000))
    mc_res = mc_engine.run()

    exposure = InvestorExposureEngine.evaluate(
        base_assumptions=base_assumptions,
        monte_carlo_summary=mc_res,
        funnel_summary={},
    )
    return {
        "success": True,
        "data": exposure,
    }


@router.post("/calculate")
async def calculate_what_if_metrics(payload: WhatIfSimulationInputs):
    """Authoritatively calculate business KPIs on backend.
    
    Inputs: Rent, Store Size, Marketing Budget, Competitor Count, Festival Season,
            Metro Opening, Inflation, Customer Segment.
    Outputs: Monthly Revenue, Expenses, Profit, Break-even Month, Customer Growth,
             Success Probability, 12-month Forecast, Profit Trend.
    """
    res = WhatIfSimulationEngine.calculate(payload)
    return {
        "success": True,
        "data": res
    }


@router.post("/what-if")
async def run_what_if(payload: Dict[str, Any]):
    """Re-run simulation with modified What-If sensitivity controls."""
    # Check if this is the advanced what-if payload with changes dict or direct fields
    changes = payload.get("changes", payload)
    
    inputs = WhatIfSimulationInputs(
        rent=float(changes.get("rent", 180000.0)),
        store_size=float(changes.get("store_size", 1200.0)),
        marketing_budget=float(changes.get("marketing_budget", 150000.0)),
        competitor_count=int(changes.get("competitor_count", 14)),
        festival_season=bool(changes.get("festival_season", False)),
        metro_opening=bool(changes.get("metro_opening", False)),
        inflation=float(changes.get("inflation", 5.0)),
        customer_segment=str(changes.get("customer_segment", "Tech Professionals")),
        category=str(changes.get("category", "Specialty Coffee")),
        locality=str(changes.get("locality", "Madhapur")),
    )
    whatif_result = WhatIfSimulationEngine.calculate(inputs)

    return {
        "success": True,
        "data": whatif_result,
        "updated_assumptions": changes,
        "monthly_revenue": whatif_result["monthly_revenue"],
        "expenses": whatif_result["expenses"],
        "profit": whatif_result["profit"],
        "break_even_month": whatif_result["break_even_month"],
        "customer_growth": whatif_result["customer_growth"],
        "success_probability": whatif_result["success_probability"],
        "forecast_12_month": whatif_result["forecast_12_month"],
        "profit_trend": whatif_result["profit_trend"],
    }


@router.post("/test-intervention")
async def test_intervention(payload: TestInterventionRequest):
    """Simulate Before vs After comparison for a specific recommendation."""
    defaults = {
        "monthly_customers_base": 500,
        "customer_acquisition_cost": 320.0,
        "average_order_value": 3499.0,
        "purchase_frequency": 1.5,
        "retention_rate": 0.40,
        "operating_cost_monthly": 185000.0,
        "marketing_budget_monthly": 150000.0,
        "gross_margin_percent": 0.55,
        "investment_amount": 3000000.0,
        "growth_rate_monthly": 0.08,
    }
    current = dict(defaults)
    if payload.current_assumptions:
        for k, v in payload.current_assumptions.items():
            if k in current:
                current[k] = float(v)

    # 1. Run baseline (Before)
    before_assumptions = SimulationAssumptions(
        deployment_model="hybrid",
        monthly_customers_base=int(current["monthly_customers_base"]),
        customer_acquisition_cost=current["customer_acquisition_cost"],
        average_order_value=current["average_order_value"],
        purchase_frequency=current["purchase_frequency"],
        retention_rate=current["retention_rate"],
        operating_cost_monthly=current["operating_cost_monthly"],
        marketing_budget_monthly=current["marketing_budget_monthly"],
        gross_margin_percent=current["gross_margin_percent"],
        investment_amount=current["investment_amount"],
        growth_rate_monthly=current.get("growth_rate_monthly", 0.08),
    )
    before_engine = VentureSimulationEngine(before_assumptions)
    before_results = before_engine.run_scenario("expected", months=payload.months)
    before_breakeven = before_engine.find_break_even(before_results)

    # 2. Compute parameter adjustments
    intervention = recommendation_engine.compute_intervention(
        recommendation=payload.recommendation,
        current_assumptions=current,
    )
    mod = intervention["modified_assumptions"]

    # 3. Run modified (After)
    after_assumptions = SimulationAssumptions(
        deployment_model="hybrid",
        monthly_customers_base=int(mod.get("monthly_customers_base", current["monthly_customers_base"])),
        customer_acquisition_cost=mod.get("customer_acquisition_cost", current["customer_acquisition_cost"]),
        average_order_value=mod.get("average_order_value", current["average_order_value"]),
        purchase_frequency=mod.get("purchase_frequency", current["purchase_frequency"]),
        retention_rate=min(0.95, mod.get("retention_rate", current["retention_rate"])),
        operating_cost_monthly=mod.get("operating_cost_monthly", current["operating_cost_monthly"]),
        marketing_budget_monthly=mod.get("marketing_budget_monthly", current["marketing_budget_monthly"]),
        gross_margin_percent=mod.get("gross_margin_percent", current["gross_margin_percent"]),
        investment_amount=mod.get("investment_amount", current["investment_amount"]),
        growth_rate_monthly=mod.get("growth_rate_monthly", current.get("growth_rate_monthly", 0.08)),
    )
    after_engine = VentureSimulationEngine(after_assumptions)
    after_results = after_engine.run_scenario("expected", months=payload.months)
    after_breakeven = after_engine.find_break_even(after_results)

    # 4. Deltas
    m12_before_rev = before_results[11].revenue if len(before_results) >= 12 else 0
    m12_after_rev = after_results[11].revenue if len(after_results) >= 12 else 0
    rev_delta = m12_after_rev - m12_before_rev
    rev_delta_pct = round((rev_delta / max(m12_before_rev, 1)) * 100, 1)

    m12_before_profit = before_results[11].net_profit if len(before_results) >= 12 else 0
    m12_after_profit = after_results[11].net_profit if len(after_results) >= 12 else 0
    profit_delta = m12_after_profit - m12_before_profit

    m12_before_cust = before_results[11].customers if len(before_results) >= 12 else 0
    m12_after_cust = after_results[11].customers if len(after_results) >= 12 else 0
    cust_delta = m12_after_cust - m12_before_cust

    impact_summary = (
        f"Testing '{payload.recommendation.get('title', 'Recommendation')}' yields "
        f"{rev_delta_pct:+.1f}% Month 12 revenue change (₹{rev_delta:+,.0f}) and "
        f"Month 12 net profit delta of ₹{profit_delta:+,.0f}. "
    )
    if after_breakeven != before_breakeven:
        impact_summary += f"Break-even shifts from Month {before_breakeven or 'N/A'} to Month {after_breakeven or 'N/A'}."

    return {
        "success": True,
        "recommendation": payload.recommendation,
        "changes_applied": intervention["changes_applied"],
        "comparison": {
            "month_12_revenue": {
                "before": m12_before_rev,
                "after": m12_after_rev,
                "delta": rev_delta,
                "delta_pct": rev_delta_pct,
            },
            "month_12_profit": {
                "before": m12_before_profit,
                "after": m12_after_profit,
                "delta": profit_delta,
            },
            "month_12_customers": {
                "before": m12_before_cust,
                "after": m12_after_cust,
                "delta": cust_delta,
            },
            "break_even_month": {
                "before": before_breakeven,
                "after": after_breakeven,
            },
        },
        "impact_summary": impact_summary,
        "before_trajectory": [{"month": r.month, "revenue": r.revenue, "profit": r.net_profit, "customers": r.customers} for r in before_results[::3]],
        "after_trajectory": [{"month": r.month, "revenue": r.revenue, "profit": r.net_profit, "customers": r.customers} for r in after_results[::3]],
    }


@router.get("/{id}")
async def get_simulation(id: str):
    """Retrieve existing simulation run results."""
    assumptions = SimulationAssumptions(
        deployment_model="hybrid",
        monthly_customers_base=500,
        customer_acquisition_cost=300.0,
        average_order_value=3500.0,
        purchase_frequency=1.5,
        retention_rate=0.40,
        operating_cost_monthly=250000.0,
        marketing_budget_monthly=150000.0,
        gross_margin_percent=0.55,
        investment_amount=3000000.0,
    )
    engine = VentureSimulationEngine(assumptions)
    results = engine.run_all_scenarios(months=24)
    explanations = explanation_agent.explain_simulation(results, assumptions)
    return {
        "success": True,
        "simulation_id": id,
        "results": results,
        "explanations": explanations,
    }
