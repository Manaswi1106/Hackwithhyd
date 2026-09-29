"""
Trajectory API Routes
Endpoints for calculating and fetching 0-24 month market trajectories.
"""

from fastapi import APIRouter
from app.trajectory.engine import TrajectoryEngine, TrajectoryAssumptions
from app.agents.explanation_agent import ExplanationAgent

router = APIRouter()
explanation_agent = ExplanationAgent()


@router.get("/{market_id}")
async def get_trajectory(market_id: str):
    """Calculate and return 0-24 month trajectory curves across scenarios."""
    engine = TrajectoryEngine(TrajectoryAssumptions())
    scenarios = engine.generate_all_scenarios(months=24)
    explanation = explanation_agent.explain_trajectory(scenarios)
    return {
        "success": True,
        "market_id": market_id,
        "scenarios": scenarios,
        "explanation": explanation,
    }
