"""
Unit tests for Synthetic Market, Monte Carlo stochastic engine, Stress Testing, and Decision Surface.
"""

import pytest
from app.simulation.synthetic_market import SyntheticMarketEngine
from app.simulation.monte_carlo import MonteCarloEngine, MonteCarloParams
from app.simulation.scenarios import StressTestEngine, DecisionSurfaceEngine, InvestorExposureEngine
from app.simulation.engine import SimulationAssumptions


def test_synthetic_market_500_cohort():
    """Verify that synthetic market generates exactly 500 calibrated participants with monotonic funnel."""
    engine = SyntheticMarketEngine(random_seed=42)
    res = engine.generate_population(
        venture_price=3499.0,
        market_median_price=2100.0,
        marketing_budget=150000.0,
    )

    assert res["total_synthetic_cohort"] == 500
    funnel = res["funnel"]
    stages = funnel["stages"]

    # Funnel stages must decrease or stay equal at each stage
    assert stages[0]["count"] == 500  # Total
    for i in range(len(stages) - 1):
        assert stages[i]["count"] >= stages[i + 1]["count"]

    # 5 customer segments exist
    segments = res["segments"]
    assert len(segments) == 5
    total_seg_pop = sum(s["population"] for s in segments)
    assert total_seg_pop == 500

    # Geographic distribution covers Hyderabad localities
    geo = res["geographic_distribution"]
    assert len(geo) >= 7
    top_locality = geo[0]
    assert top_locality["locality"] in ("Gachibowli", "Madhapur", "Kondapur")

    # Derived CAC calculation
    acq = res["acquisition_model"]
    assert acq["derived_blended_cac"] > 0
    assert acq["modeled_monthly_acquired_customers"] > 0


def test_monte_carlo_percentiles_and_distribution():
    """Verify Monte Carlo runs 5,000 iterations and generates valid percentile bands."""
    params = MonteCarloParams(
        monthly_customers_base=400,
        customer_acquisition_cost=250.0,
        average_order_value=3000.0,
        purchase_frequency=1.6,
        retention_rate=0.45,
        runs=5000,
        random_seed=123,
    )
    engine = MonteCarloEngine(params)
    res = engine.run()

    assert res["total_runs"] == 5000
    rev12 = res["percentiles"]["month_12_revenue"]
    assert rev12["p10"] <= rev12["p25"] <= rev12["p50"] <= rev12["p75"] <= rev12["p90"]
    assert res["probabilities"]["breakeven_within_24_months_pct"] >= 0.0
    assert len(res["tornado_sensitivities"]) == 5
    assert len(res["distribution_histograms"]["month_12_revenue"]) == 8


def test_stress_test_engine():
    """Verify that adverse shocks delay or worsen break-even vs baseline."""
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
    res = StressTestEngine.evaluate_stress_test(assumptions)

    assert "baseline" in res
    assert len(res["scenarios"]) == 5
    # The compound shock should decrease month 12 cumulative profit
    compound = next(s for s in res["scenarios"] if s["id"] == "severe_compound_shock")
    assert compound["profit_impact_inr"] < 0


def test_decision_surface_grid():
    """Verify Decision Surface generates grid of points with zone classifications."""
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
    res = DecisionSurfaceEngine.generate_surface(assumptions)

    # 7 prices x 5 budgets = 35 grid points
    assert len(res["points"]) == 35
    assert res["recommended_envelope"]["price_range"]
