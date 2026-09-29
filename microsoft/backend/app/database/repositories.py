"""
Database Repositories for VentureScope Platform
Provides clean CRUD and query interfaces for all entities.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from sqlalchemy import select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import (
    User, Market, Venture, Competitor, Product, Location,
    LocationMetric, CustomerSegment, SimulationRun, SimulationAssumption,
    SimulationResult, AnalysisRun, MarketEvent, Evidence, Source
)


class MarketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, market_id: str) -> Optional[Market]:
        result = await self.session.execute(select(Market).where(Market.id == market_id))
        return result.scalars().first()

    async def get_or_create(
        self,
        city_id: str,
        city_name: str,
        category_id: str,
        subcategory_id: str,
        category_name: str,
        subcategory_name: str,
    ) -> Market:
        market_id = f"{city_id}_{category_id}_{subcategory_id}".lower()
        market = await self.get_by_id(market_id)
        if not market:
            market = Market(
                id=market_id,
                city_id=city_id,
                city_name=city_name,
                category_id=category_id,
                subcategory_id=subcategory_id,
                category_name=category_name,
                subcategory_name=subcategory_name,
            )
            self.session.add(market)
            await self.session.commit()
            await self.session.refresh(market)
        return market


class CompetitorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_market(self, market_id: str) -> List[Competitor]:
        result = await self.session.execute(
            select(Competitor).where(Competitor.market_id == market_id)
        )
        return list(result.scalars().all())

    async def add_competitor(self, competitor_data: Dict[str, Any]) -> Competitor:
        comp_id = competitor_data.get("id") or f"comp_{uuid.uuid4().hex[:8]}"
        competitor = Competitor(
            id=comp_id,
            market_id=competitor_data["market_id"],
            name=competitor_data["name"],
            category=competitor_data.get("category", "General"),
            positioning=competitor_data.get("positioning", "mid-range"),
            price_min=competitor_data.get("price_min", 0.0),
            price_max=competitor_data.get("price_max", 0.0),
            target_audience=competitor_data.get("target_audience", []),
            customer_segments=competitor_data.get("customer_segments", []),
            major_locations=competitor_data.get("major_locations", []),
            popular_products=competitor_data.get("popular_products", []),
            evidence_type=competitor_data.get("evidence_type", "observed"),
            source_url=competitor_data.get("source_url"),
            confidence=competitor_data.get("confidence", "high"),
            position_x=competitor_data.get("position_x", 50.0),
            position_y=competitor_data.get("position_y", 50.0),
        )
        self.session.add(competitor)
        await self.session.commit()
        await self.session.refresh(competitor)
        return competitor


class LocationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_metrics_by_market(self, market_id: str) -> List[LocationMetric]:
        result = await self.session.execute(
            select(LocationMetric).where(LocationMetric.market_id == market_id)
        )
        return list(result.scalars().all())


class AnalysisRunRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_run(self, market_id: str, venture_id: Optional[str] = None) -> AnalysisRun:
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        run = AnalysisRun(
            id=run_id,
            market_id=market_id,
            venture_id=venture_id,
            status="researching",
            progress=10,
            stages=[
                {"name": "Market Discovery", "status": "running", "description": "Extracting public market signals"},
                {"name": "Competitor Analysis", "status": "pending", "description": "Profiling top market competitors"},
                {"name": "Customer Demand Modeling", "status": "pending", "description": "Synthesizing demographic segments"},
                {"name": "Venture Fit Assessment", "status": "pending", "description": "Analyzing venture positioning & gaps"},
                {"name": "Hindsight Memory Synchronization", "status": "pending", "description": "Comparing with previous analyses"},
                {"name": "Deterministic Simulation", "status": "pending", "description": "Calculating 24-month financial scenarios"},
            ]
        )
        self.session.add(run)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def get_by_id(self, run_id: str) -> Optional[AnalysisRun]:
        result = await self.session.execute(select(AnalysisRun).where(AnalysisRun.id == run_id))
        return result.scalars().first()

    async def update_status(self, run_id: str, status: str, progress: int, summary: Optional[str] = None):
        values = {"status": status, "progress": progress}
        if summary:
            values["summary"] = summary
        if status == "complete":
            values["completed_at"] = datetime.now(timezone.utc)
        await self.session.execute(
            update(AnalysisRun).where(AnalysisRun.id == run_id).values(**values)
        )
        await self.session.commit()
