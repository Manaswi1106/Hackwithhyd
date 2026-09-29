"""
Tests for Market Trajectory Engine
Verifies 0-24 month projection curve math, scenario ranges, and assumption parameterization.
"""

import pytest
from app.trajectory.engine import TrajectoryEngine, TrajectoryAssumptions


def test_trajectory_projection_points():
    """Verify trajectory yields points at 3-month increments from month 0 to 24."""
    assumptions = TrajectoryAssumptions(
        demand_growth_rate=0.05,
        competition_growth_rate=0.03,
        price_change_rate=0.01,
        customer_growth_rate=0.04,
        base_demand=100.0,
        base_competition=10.0,
        base_price=1500.0,
    )

    engine = TrajectoryEngine(assumptions)
    expected_points = engine.generate_trajectory("expected", months=24)

    assert len(expected_points) == 9  # 0, 3, 6, 9, 12, 15, 18, 21, 24
    assert expected_points[0]["month"] == 0
    assert expected_points[-1]["month"] == 24
    assert expected_points[0]["demand"] == 100.0


def test_trajectory_scenarios():
    """Verify scenario ordering: optimistic demand > expected demand > pessimistic demand."""
    engine = TrajectoryEngine(TrajectoryAssumptions())
    scenarios = engine.generate_all_scenarios(months=24)

    opt_final = scenarios["optimistic"][-1]["demand"]
    exp_final = scenarios["expected"][-1]["demand"]
    pess_final = scenarios["pessimistic"][-1]["demand"]

    assert opt_final > exp_final > pess_final
    assert len(scenarios["drivers"]) >= 3
