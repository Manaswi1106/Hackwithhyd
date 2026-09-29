"""
API Endpoint Integration Tests
Verifies FastAPI routing, payload schemas, and response contracts.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_root_and_health():
    """Verify API root and health endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/")
        assert res.status_code == 200
        assert res.json()["name"] == "VentureScope API"

        res_health = await client.get("/health")
        assert res_health.status_code == 200
        assert res_health.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_market_endpoints():
    """Verify market pulse, competitors, and trajectory endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Market pulse
        res_pulse = await client.get("/api/markets/hyderabad_fashion_footwear/pulse")
        assert res_pulse.status_code == 200
        assert res_pulse.json()["success"] is True
        assert "demand_trend" in res_pulse.json()["data"]

        # Competitors
        res_comp = await client.get("/api/markets/hyderabad_fashion_footwear/competitors")
        assert res_comp.status_code == 200
        assert len(res_comp.json()["data"]) >= 5

        # Trajectory
        res_traj = await client.get("/api/markets/hyderabad_fashion_footwear/trajectory")
        assert res_traj.status_code == 200
        assert "scenarios" in res_traj.json()["data"]


@pytest.mark.asyncio
async def test_simulation_endpoints():
    """Verify simulation execution and What-If endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Run simulation
        payload = {
            "deployment_model": "hybrid",
            "monthly_customers": 600,
            "customer_acquisition_cost": 280.0,
            "average_order_value": 3200.0,
            "purchase_frequency": 1.5,
            "retention_rate": 0.45,
            "operating_cost_monthly": 200000.0,
            "marketing_budget_monthly": 120000.0,
            "gross_margin_percent": 0.58,
            "investment_amount": 2500000.0,
        }
        res_sim = await client.post("/api/simulation/run", json=payload)
        assert res_sim.status_code == 200
        data = res_sim.json()
        assert "results" in data
        assert "optimistic" in data["results"]
        assert "expected" in data["results"]
        assert "pessimistic" in data["results"]


@pytest.mark.asyncio
async def test_hindsight_endpoints():
    """Verify Hindsight 'What Changed?' and timeline routes."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res_changes = await client.get("/api/hindsight/target_venture/changes")
        assert res_changes.status_code == 200
        data = res_changes.json()
        assert "changes" in data
        assert len(data["changes"]) > 0

        res_timeline = await client.get("/api/hindsight/target_venture/timeline")
        assert res_timeline.status_code == 200
        assert len(res_timeline.json()["timeline"]) >= 2
