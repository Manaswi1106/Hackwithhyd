"""
Tests for Deterministic Financial Simulation Engine
Verifies break-even finding, runway calculation, and optimistic/expected/pessimistic reproducibility.
"""

import pytest
from app.simulation.engine import SimulationAssumptions, VentureSimulationEngine


def test_deterministic_simulation_reproducibility():
    """Verify that the financial simulation is 100% deterministic (no random LLM output)."""
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

    engine1 = VentureSimulationEngine(assumptions)
    results1 = engine1.run_all_scenarios(months=24)

    engine2 = VentureSimulationEngine(assumptions)
    results2 = engine2.run_all_scenarios(months=24)

    # Identical inputs must yield strictly identical outputs
    assert results1["expected"]["months"][11]["revenue"] == results2["expected"]["months"][11]["revenue"]
    assert results1["expected"]["months"][11]["profit"] == results2["expected"]["months"][11]["profit"]
    assert results1["expected"]["break_even_month"] == results2["expected"]["break_even_month"]


def test_scenario_hierarchy():
    """Verify Optimistic revenue > Expected revenue > Pessimistic revenue."""
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

    m12_opt = results["optimistic"]["months"][11]["revenue"]
    m12_exp = results["expected"]["months"][11]["revenue"]
    m12_pess = results["pessimistic"]["months"][11]["revenue"]

    assert m12_opt > m12_exp > m12_pess


def test_break_even_calculation():
    """Verify break-even identification logic."""
    assumptions = SimulationAssumptions(
        deployment_model="online",
        monthly_customers_base=1000,
        customer_acquisition_cost=150.0,
        average_order_value=4000.0,
        purchase_frequency=2.0,
        retention_rate=0.60,
        operating_cost_monthly=100000.0,
        marketing_budget_monthly=100000.0,
        gross_margin_percent=0.70,
        investment_amount=1000000.0,
    )

    engine = VentureSimulationEngine(assumptions)
    results = engine.run_scenario("expected", months=24)
    break_even = engine.find_break_even(results)

    assert break_even is not None
    assert 1 <= break_even <= 24
    # The month before break_even should have cumulative profit < 0
    if break_even > 1:
        assert results[break_even - 2].cumulative_profit < 0
    assert results[break_even - 1].cumulative_profit >= 0
