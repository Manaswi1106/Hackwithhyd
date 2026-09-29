import os

base_dir = r'c:\Users\sahas\OneDrive\Desktop\microsoft\backend'

dirs = [
    'app/api/routes',
    'app/agents',
    'app/hindsight',
    'app/rag',
    'app/simulation',
    'app/trajectory',
    'app/database',
    'app/services',
    'app/schemas',
    'app/tests'
]

files = {
    'requirements.txt': '''fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
pydantic-settings==2.5.2
sqlalchemy==2.0.35
alembic==1.13.3
asyncpg==0.29.0
pgvector==0.3.5
httpx==0.27.2
python-dotenv==1.0.1
langgraph==0.2.34
langchain==0.3.3
langchain-core==0.3.10
langchain-groq==0.2.0
python-multipart==0.0.12
cors==1.0.1
''',
    '.env.example': '''# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/venturescope

# Hindsight by Vectorize
HINDSIGHT_API_KEY=
HINDSIGHT_ORG_ID=
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io

# LLM Provider (Groq)
GROQ_API_KEY=

# Maps
MAPBOX_TOKEN=

# Auth
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# App
APP_ENV=development
DEBUG=true
''',
    'app/__init__.py': '',
    'app/api/__init__.py': '',
    'app/api/deps.py': '',
    'app/api/routes/__init__.py': '',
    'app/agents/__init__.py': '',
    'app/agents/orchestrator.py': '',
    'app/agents/market_agent.py': '',
    'app/agents/competitor_agent.py': '',
    'app/agents/customer_agent.py': '',
    'app/agents/venture_agent.py': '',
    'app/agents/evidence_agent.py': '',
    'app/agents/opportunity_agent.py': '',
    'app/agents/simulation_agent.py': '',
    'app/agents/explanation_agent.py': '',
    'app/hindsight/__init__.py': '',
    'app/hindsight/client.py': '',
    'app/hindsight/memory_schemas.py': '',
    'app/hindsight/retrieval.py': '',
    'app/rag/__init__.py': '',
    'app/rag/embeddings.py': '',
    'app/rag/retrieval.py': '',
    'app/rag/document_store.py': '',
    'app/simulation/__init__.py': '',
    'app/simulation/assumptions.py': '',
    'app/simulation/scenarios.py': '',
    'app/simulation/financial_model.py': '',
    'app/trajectory/__init__.py': '',
    'app/trajectory/assumptions.py': '',
    'app/database/__init__.py': '',
    'app/database/models.py': '',
    'app/database/connection.py': '',
    'app/database/repositories.py': '',
    'app/services/__init__.py': '',
    'app/services/research.py': '',
    'app/services/web_sources.py': '',
    'app/services/evidence.py': '',
    'app/schemas/__init__.py': '',
    'app/tests/__init__.py': '',
    'app/config.py': '''from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/venturescope"
    
    # Hindsight
    hindsight_api_key: Optional[str] = None
    hindsight_org_id: Optional[str] = None
    hindsight_base_url: str = "https://api.hindsight.vectorize.io"
    
    # LLM
    groq_api_key: Optional[str] = None
    
    # Maps
    mapbox_token: Optional[str] = None
    
    # Auth
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    
    # App
    app_env: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
''',
    'app/main.py': '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import analysis, markets, ventures, competitors, simulation, trajectory, maps, customers, hindsight_routes
from app.config import settings

app = FastAPI(
    title="VentureScope API",
    description="Venture Intelligence Platform - Evidence-grounded market analysis and venture simulation",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(markets.router, prefix="/api/markets", tags=["Markets"])
app.include_router(ventures.router, prefix="/api/ventures", tags=["Ventures"])
app.include_router(competitors.router, prefix="/api/competitors", tags=["Competitors"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(trajectory.router, prefix="/api/trajectory", tags=["Trajectory"])
app.include_router(maps.router, prefix="/api/maps", tags=["Maps"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(hindsight_routes.router, prefix="/api/hindsight", tags=["Hindsight"])

@app.get("/")
async def root():
    return {
        "name": "VentureScope API",
        "version": "0.1.0",
        "status": "operational",
        "description": "Evidence-grounded venture intelligence platform"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "env": settings.app_env}
''',
    'app/schemas/common.py': '''from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum

class EvidenceType(str, Enum):
    OBSERVED = "observed"
    INFERRED = "inferred"
    MODELED = "modeled"
    SIMULATED = "simulated"

class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INSUFFICIENT = "insufficient"

class Scenario(str, Enum):
    OPTIMISTIC = "optimistic"
    EXPECTED = "expected"
    PESSIMISTIC = "pessimistic"

class EvidenceSource(BaseModel):
    id: str
    url: Optional[str] = None
    name: str
    retrieved_at: datetime
    evidence_type: EvidenceType
    confidence: ConfidenceLevel

class EvidencedMetric(BaseModel):
    value: Any
    source: Optional[EvidenceSource] = None
    confidence: ConfidenceLevel
    evidence_type: EvidenceType
    timestamp: datetime
    assumptions: Optional[List[str]] = None

class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
''',
    'app/schemas/market.py': '''from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from .common import EvidencedMetric, EvidenceType, ConfidenceLevel

class MarketCreate(BaseModel):
    city_id: str
    category_id: str
    subcategory_id: str
    venture_name: Optional[str] = None
    venture_url: Optional[str] = None
    venture_description: Optional[str] = None

class MarketResponse(BaseModel):
    id: str
    city_id: str
    city_name: str
    category_id: str
    subcategory_id: str
    category_name: str
    subcategory_name: str
    created_at: datetime

class MarketPulse(BaseModel):
    demand_trend: EvidencedMetric
    competition_trend: EvidencedMetric
    average_price: EvidencedMetric
    search_trend: EvidencedMetric
    market_growth_signal: EvidencedMetric

class LocationMetrics(BaseModel):
    location_id: str
    name: str
    lat: float
    lng: float
    competitor_density: EvidencedMetric
    customer_concentration: EvidencedMetric
    demand_signal: EvidencedMetric
    average_price: EvidencedMetric
    opportunity_signal: EvidencedMetric
    target_audience: List[str]
    observed_activity: EvidencedMetric

class MapHeatmapData(BaseModel):
    locations: List[LocationMetrics]
    bounds: Dict[str, float]
    default_center: Dict[str, float]
    default_zoom: int

class TrajectoryPoint(BaseModel):
    month: int
    demand: float
    competition: float
    average_price: float
    customer_growth: float
    opportunity_signal: float

class TrajectoryDriver(BaseModel):
    name: str
    direction: str  # increasing, stable, decreasing
    impact: str  # high, medium, low
    explanation: str

class MarketTrajectory(BaseModel):
    optimistic: List[TrajectoryPoint]
    expected: List[TrajectoryPoint]
    pessimistic: List[TrajectoryPoint]
    assumptions: Dict[str, str]
    drivers: List[TrajectoryDriver]
''',
    'app/schemas/competitor.py': '''from pydantic import BaseModel
from typing import Optional, List, Dict
from .common import EvidenceType, EvidenceSource

class CompetitorResponse(BaseModel):
    id: str
    name: str
    category: str
    price_range: Dict[str, float]  # {min, max}
    positioning: str
    target_audience: List[str]
    customer_segments: List[str]
    major_locations: List[str]
    popular_products: List[str]
    evidence_type: EvidenceType
    source: Optional[EvidenceSource] = None
    map_position: Optional[Dict[str, float]] = None
''',
    'app/schemas/venture.py': '''from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from .common import EvidencedMetric

class VentureAnalyzeRequest(BaseModel):
    url: str
    market_id: str

class VentureXRay(BaseModel):
    business_model: EvidencedMetric
    product: EvidencedMetric
    price: EvidencedMetric
    target_audience: EvidencedMetric
    positioning: EvidencedMetric
    differentiators: List[str]
    competitive_overlap: List[str]
    strength_signals: List[str]
    risk_signals: List[str]
''',
    'app/schemas/simulation_schema.py': '''from pydantic import BaseModel
from typing import Optional, List, Dict
from .common import Scenario

class SimulationRequest(BaseModel):
    market_id: str
    venture_id: Optional[str] = None
    deployment_model: str = "hybrid"  # online, physical, hybrid, multi-location
    target_location: Optional[str] = None
    monthly_customers: int = 500
    customer_acquisition_cost: float = 200.0
    average_order_value: float = 1500.0
    purchase_frequency: float = 2.0
    retention_rate: float = 0.6
    operating_cost_monthly: float = 200000.0
    marketing_budget_monthly: float = 100000.0
    gross_margin_percent: float = 0.55
    investment_amount: float = 2000000.0

class WhatIfRequest(BaseModel):
    simulation_id: str
    changes: Dict[str, float]  # field_name -> new_value

class SimulationMonth(BaseModel):
    month: int
    customers: int
    revenue: float
    costs: float
    profit: float
    cumulative_profit: float
    cumulative_investment: float

class SimulationScenarioResult(BaseModel):
    scenario: Scenario
    months: List[SimulationMonth]
    break_even_month: Optional[int] = None
    total_investment_required: float
    recovery_month: Optional[int] = None

class SimulationResponse(BaseModel):
    id: str
    market_id: str
    venture_id: Optional[str] = None
    assumptions: Dict[str, float]
    results: List[SimulationScenarioResult]
''',
    'app/simulation/engine.py': '''from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math

@dataclass
class SimulationAssumptions:
    deployment_model: str
    monthly_customers_base: int
    customer_acquisition_cost: float
    average_order_value: float
    purchase_frequency: float
    retention_rate: float
    operating_cost_monthly: float
    marketing_budget_monthly: float
    gross_margin_percent: float
    investment_amount: float
    growth_rate_monthly: float = 0.08  # 8% monthly customer growth
    churn_rate: float = 0.05
    target_location: Optional[str] = None

@dataclass
class MonthResult:
    month: int
    customers: int
    new_customers: int
    returning_customers: int
    revenue: float
    cogs: float
    gross_profit: float
    operating_costs: float
    marketing_costs: float
    total_costs: float
    net_profit: float
    cumulative_profit: float
    cumulative_investment: float
    burn_rate: float
    runway_months: float

class VentureSimulationEngine:
    """Deterministic financial simulation engine.
    
    The LLM does NOT calculate financial numbers.
    This engine takes structured assumptions and produces
    reproducible financial projections.
    """
    
    def __init__(self, assumptions: SimulationAssumptions):
        self.assumptions = assumptions
    
    def run_scenario(self, scenario: str, months: int = 24) -> List[MonthResult]:
        """Run a single scenario simulation."""
        multipliers = {
            'optimistic': {'growth': 1.3, 'retention': 1.15, 'aov': 1.1, 'cost': 0.9},
            'expected': {'growth': 1.0, 'retention': 1.0, 'aov': 1.0, 'cost': 1.0},
            'pessimistic': {'growth': 0.7, 'retention': 0.85, 'aov': 0.9, 'cost': 1.15},
        }
        m = multipliers.get(scenario, multipliers['expected'])
        
        results = []
        cumulative_profit = 0.0
        cumulative_investment = self.assumptions.investment_amount
        total_customer_base = 0
        
        for month in range(1, months + 1):
            # Customer calculations
            growth_rate = self.assumptions.growth_rate_monthly * m['growth']
            retention = self.assumptions.retention_rate * m['retention']
            retention = min(retention, 0.95)  # Cap at 95%
            
            if month == 1:
                new_customers = self.assumptions.monthly_customers_base
                returning_customers = 0
            else:
                new_customers = int(
                    self.assumptions.monthly_customers_base * (1 + growth_rate) ** (month - 1)
                )
                returning_customers = int(total_customer_base * retention * (1 - self.assumptions.churn_rate))
            
            total_customers = new_customers + returning_customers
            total_customer_base = total_customers
            
            # Revenue
            aov = self.assumptions.average_order_value * m['aov']
            revenue = total_customers * aov * self.assumptions.purchase_frequency
            
            # Costs
            cogs = revenue * (1 - self.assumptions.gross_margin_percent)
            gross_profit = revenue - cogs
            operating = self.assumptions.operating_cost_monthly * m['cost']
            marketing = self.assumptions.marketing_budget_monthly * m['cost']
            cac_costs = new_customers * self.assumptions.customer_acquisition_cost
            total_costs = cogs + operating + marketing + cac_costs
            
            # Profit
            net_profit = revenue - total_costs
            cumulative_profit += net_profit
            
            # Burn & Runway
            burn_rate = max(0, -net_profit)
            remaining_funds = max(0, cumulative_investment + cumulative_profit)
            runway = remaining_funds / burn_rate if burn_rate > 0 else float('inf')
            
            results.append(MonthResult(
                month=month,
                customers=total_customers,
                new_customers=new_customers,
                returning_customers=returning_customers,
                revenue=round(revenue, 2),
                cogs=round(cogs, 2),
                gross_profit=round(gross_profit, 2),
                operating_costs=round(operating, 2),
                marketing_costs=round(marketing, 2),
                total_costs=round(total_costs, 2),
                net_profit=round(net_profit, 2),
                cumulative_profit=round(cumulative_profit, 2),
                cumulative_investment=round(cumulative_investment, 2),
                burn_rate=round(burn_rate, 2),
                runway_months=round(min(runway, 999), 1),
            ))
        
        return results
    
    def find_break_even(self, results: List[MonthResult]) -> Optional[int]:
        """Find the month where cumulative profit turns positive."""
        for r in results:
            if r.cumulative_profit >= 0:
                return r.month
        return None
    
    def find_investment_recovery(self, results: List[MonthResult]) -> Optional[int]:
        """Find the month where cumulative profit exceeds initial investment."""
        for r in results:
            if r.cumulative_profit >= self.assumptions.investment_amount:
                return r.month
        return None
    
    def run_all_scenarios(self, months: int = 24) -> Dict[str, dict]:
        """Run optimistic, expected, and pessimistic scenarios."""
        output = {}
        for scenario in ['optimistic', 'expected', 'pessimistic']:
            results = self.run_scenario(scenario, months)
            output[scenario] = {
                'months': [{
                    'month': r.month,
                    'customers': r.customers,
                    'revenue': r.revenue,
                    'costs': r.total_costs,
                    'profit': r.net_profit,
                    'cumulative_profit': r.cumulative_profit,
                    'cumulative_investment': r.cumulative_investment,
                } for r in results],
                'break_even_month': self.find_break_even(results),
                'recovery_month': self.find_investment_recovery(results),
                'total_investment_required': self.assumptions.investment_amount,
                'final_month': {
                    'customers': results[-1].customers,
                    'revenue': results[-1].revenue,
                    'burn_rate': results[-1].burn_rate,
                    'runway_months': results[-1].runway_months,
                    'net_profit': results[-1].net_profit,
                } if results else None
            }
        return output
''',
    'app/trajectory/engine.py': '''from typing import Dict, List, Optional
from dataclasses import dataclass
import math

@dataclass
class TrajectoryAssumptions:
    demand_growth_rate: float = 0.05  # 5% monthly
    competition_growth_rate: float = 0.03  # 3% monthly
    price_change_rate: float = 0.01  # 1% monthly
    customer_growth_rate: float = 0.04  # 4% monthly
    base_demand: float = 100.0
    base_competition: float = 10.0
    base_price: float = 1500.0
    base_customer_index: float = 100.0

class TrajectoryEngine:
    """Deterministic market trajectory engine.
    
    Generates 0-24 month projections based on structured assumptions.
    The LLM provides assumptions; this engine calculates trajectories.
    """
    
    def __init__(self, assumptions: TrajectoryAssumptions):
        self.assumptions = assumptions
    
    def generate_trajectory(self, scenario: str, months: int = 24) -> List[dict]:
        multipliers = {
            'optimistic': {'demand': 1.4, 'competition': 0.8, 'price': 1.1, 'growth': 1.3},
            'expected': {'demand': 1.0, 'competition': 1.0, 'price': 1.0, 'growth': 1.0},
            'pessimistic': {'demand': 0.6, 'competition': 1.3, 'price': 0.9, 'growth': 0.7},
        }
        m = multipliers.get(scenario, multipliers['expected'])
        
        points = []
        for month in range(0, months + 1, 3):
            t = month / 12.0  # Time in years
            
            demand = self.assumptions.base_demand * (
                1 + self.assumptions.demand_growth_rate * m['demand']
            ) ** month
            
            competition = self.assumptions.base_competition * (
                1 + self.assumptions.competition_growth_rate * m['competition']
            ) ** month
            
            avg_price = self.assumptions.base_price * (
                1 + self.assumptions.price_change_rate * m['price']
            ) ** month
            
            customer_growth = self.assumptions.base_customer_index * (
                1 + self.assumptions.customer_growth_rate * m['growth']
            ) ** month
            
            # Opportunity signal: higher demand + lower competition = higher opportunity
            opportunity = (demand / max(competition, 1)) * 10
            opportunity = min(opportunity, 100)
            
            points.append({
                'month': month,
                'demand': round(demand, 1),
                'competition': round(competition, 1),
                'average_price': round(avg_price, 0),
                'customer_growth': round(customer_growth, 1),
                'opportunity_signal': round(opportunity, 1),
            })
        
        return points
    
    def generate_all_scenarios(self, months: int = 24) -> dict:
        return {
            'optimistic': self.generate_trajectory('optimistic', months),
            'expected': self.generate_trajectory('expected', months),
            'pessimistic': self.generate_trajectory('pessimistic', months),
            'assumptions': {
                'demand_growth_rate': str(self.assumptions.demand_growth_rate),
                'competition_growth_rate': str(self.assumptions.competition_growth_rate),
                'price_change_rate': str(self.assumptions.price_change_rate),
                'customer_growth_rate': str(self.assumptions.customer_growth_rate),
            },
            'drivers': [
                {
                    'name': 'Market Demand',
                    'direction': 'increasing',
                    'impact': 'high',
                    'explanation': 'Growing consumer interest in the category based on search and activity signals'
                },
                {
                    'name': 'Competition',
                    'direction': 'increasing',
                    'impact': 'medium',
                    'explanation': 'New entrants entering the market at a moderate pace'
                },
                {
                    'name': 'Average Price',
                    'direction': 'stable',
                    'impact': 'low',
                    'explanation': 'Prices relatively stable with minor upward pressure'
                },
                {
                    'name': 'Customer Concentration',
                    'direction': 'increasing',
                    'impact': 'high',
                    'explanation': 'Target demographic growing in key Hyderabad areas'
                },
            ]
        }
''',
    'app/hindsight/providers.py': '''from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime

class HindsightProvider(ABC):
    """Abstract provider interface for Hindsight memory system.
    
    This abstraction allows swapping between real Hindsight SDK
    and a mock provider for local development.
    """
    
    @abstractmethod
    async def retain(self, namespace: str, content: str, metadata: Dict[str, Any]) -> str:
        """Store a memory/observation in Hindsight."""
        pass
    
    @abstractmethod
    async def recall(self, namespace: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve relevant memories from Hindsight."""
        pass
    
    @abstractmethod
    async def reflect(self, namespace: str, query: str) -> str:
        """Get a synthesized reflection from stored memories."""
        pass


class MockHindsightProvider(HindsightProvider):
    """Mock provider for local development without Hindsight credentials.
    
    WARNING: This is ONLY for local development.
    Production/hackathon demo MUST use RealHindsightProvider.
    """
    
    def __init__(self):
        self._memories: Dict[str, List[Dict[str, Any]]] = {}
    
    async def retain(self, namespace: str, content: str, metadata: Dict[str, Any]) -> str:
        if namespace not in self._memories:
            self._memories[namespace] = []
        
        memory_id = f"mock_{namespace}_{len(self._memories[namespace])}"
        self._memories[namespace].append({
            'id': memory_id,
            'content': content,
            'metadata': metadata,
            'timestamp': datetime.utcnow().isoformat(),
        })
        return memory_id
    
    async def recall(self, namespace: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        memories = self._memories.get(namespace, [])
        # Simple keyword matching for mock
        query_lower = query.lower()
        scored = []
        for mem in memories:
            content_lower = mem['content'].lower()
            score = sum(1 for word in query_lower.split() if word in content_lower)
            if score > 0:
                scored.append((score, mem))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored[:limit]]
    
    async def reflect(self, namespace: str, query: str) -> str:
        memories = await self.recall(namespace, query, limit=5)
        if not memories:
            return "No previous observations found for this query."
        summaries = [m['content'][:200] for m in memories]
        return f"Based on {len(memories)} previous observations: " + "; ".join(summaries)


class RealHindsightProvider(HindsightProvider):
    """Real Hindsight SDK integration.
    
    Uses the actual Hindsight by Vectorize API.
    Requires HINDSIGHT_API_KEY and HINDSIGHT_ORG_ID.
    """
    
    def __init__(self, api_key: str, org_id: str, base_url: str = "https://api.hindsight.vectorize.io"):
        self.api_key = api_key
        self.org_id = org_id
        self.base_url = base_url
        # Will be initialized with actual Hindsight SDK
        self._client = None
    
    async def _ensure_client(self):
        if self._client is None:
            import httpx
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "X-Organization-ID": self.org_id,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
    
    async def retain(self, namespace: str, content: str, metadata: Dict[str, Any]) -> str:
        await self._ensure_client()
        response = await self._client.post(
            "/v1/retain",
            json={
                "namespace": namespace,
                "content": content,
                "metadata": metadata,
            }
        )
        response.raise_for_status()
        data = response.json()
        return data.get("id", "")
    
    async def recall(self, namespace: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        await self._ensure_client()
        response = await self._client.post(
            "/v1/recall",
            json={
                "namespace": namespace,
                "query": query,
                "limit": limit,
            }
        )
        response.raise_for_status()
        return response.json().get("memories", [])
    
    async def reflect(self, namespace: str, query: str) -> str:
        await self._ensure_client()
        response = await self._client.post(
            "/v1/reflect",
            json={
                "namespace": namespace,
                "query": query,
            }
        )
        response.raise_for_status()
        return response.json().get("reflection", "")
''',
    'app/hindsight/memory_service.py': '''from typing import Any, Dict, List, Optional
from datetime import datetime
from .providers import HindsightProvider
import json

class HindsightMemoryService:
    """Central memory service for the VentureScope platform.
    
    Stores and retrieves market intelligence using Hindsight.
    This is NOT a simple database wrapper - it's a semantic memory system
    that understands market context and can detect changes.
    """
    
    def __init__(self, provider: HindsightProvider):
        self.provider = provider
    
    # ========== RETAIN OPERATIONS ==========
    
    async def remember_market_state(self, market_id: str, state: Dict[str, Any]) -> str:
        """Store a market state observation."""
        content = (
            f"Market state for {state.get('category', 'unknown')} / {state.get('subcategory', 'unknown')} "
            f"in {state.get('city', 'unknown')}: "
            f"Competitors: {state.get('competitor_count', 'unknown')}. "
            f"Average price: {state.get('average_price', 'unknown')}. "
            f"Demand signal: {state.get('demand_signal', 'unknown')}. "
            f"Top locations: {', '.join(state.get('top_locations', []))}."
        )
        metadata = {
            'type': 'market_state',
            'market_id': market_id,
            'timestamp': datetime.utcnow().isoformat(),
            **state,
        }
        return await self.provider.retain(f"market_{market_id}", content, metadata)
    
    async def remember_competitor(self, market_id: str, competitor: Dict[str, Any]) -> str:
        """Store a competitor observation."""
        content = (
            f"Competitor: {competitor.get('name', 'unknown')}. "
            f"Price range: {competitor.get('price_range', 'unknown')}. "
            f"Positioning: {competitor.get('positioning', 'unknown')}. "
            f"Locations: {', '.join(competitor.get('locations', []))}. "
            f"Target audience: {', '.join(competitor.get('target_audience', []))}."
        )
        metadata = {
            'type': 'competitor',
            'market_id': market_id,
            'competitor_name': competitor.get('name', ''),
            'timestamp': datetime.utcnow().isoformat(),
            **competitor,
        }
        return await self.provider.retain(f"market_{market_id}", content, metadata)
    
    async def remember_customer_insight(self, market_id: str, insight: Dict[str, Any]) -> str:
        """Store a customer segment insight."""
        content = (
            f"Customer segment: {insight.get('segment', 'unknown')}. "
            f"Demand: {insight.get('demand_signal', 'unknown')}. "
            f"Typical spend: {insight.get('typical_spend', 'unknown')}. "
            f"Price sensitivity: {insight.get('price_sensitivity', 'unknown')}."
        )
        metadata = {
            'type': 'customer_insight',
            'market_id': market_id,
            'timestamp': datetime.utcnow().isoformat(),
            **insight,
        }
        return await self.provider.retain(f"market_{market_id}", content, metadata)
    
    async def remember_venture_analysis(self, venture_id: str, analysis: Dict[str, Any]) -> str:
        """Store a venture analysis result."""
        content = (
            f"Venture analysis: {analysis.get('name', 'unknown')}. "
            f"Business model: {analysis.get('business_model', 'unknown')}. "
            f"Price: {analysis.get('price', 'unknown')}. "
            f"Positioning: {analysis.get('positioning', 'unknown')}. "
            f"Target audience: {analysis.get('target_audience', 'unknown')}."
        )
        metadata = {
            'type': 'venture_analysis',
            'venture_id': venture_id,
            'timestamp': datetime.utcnow().isoformat(),
            **analysis,
        }
        return await self.provider.retain(f"venture_{venture_id}", content, metadata)
    
    async def remember_simulation(self, venture_id: str, simulation: Dict[str, Any]) -> str:
        """Store simulation results."""
        content = (
            f"Simulation for venture {venture_id}: "
            f"Expected break-even: month {simulation.get('break_even_month', 'N/A')}. "
            f"Expected revenue at month 12: {simulation.get('revenue_month_12', 'N/A')}. "
            f"Investment required: {simulation.get('investment_required', 'N/A')}."
        )
        metadata = {
            'type': 'simulation',
            'venture_id': venture_id,
            'timestamp': datetime.utcnow().isoformat(),
            **simulation,
        }
        return await self.provider.retain(f"venture_{venture_id}", content, metadata)
    
    # ========== RECALL OPERATIONS ==========
    
    async def recall_market_context(self, market_id: str, query: str = "market state") -> List[Dict[str, Any]]:
        """Retrieve previous market observations."""
        return await self.provider.recall(f"market_{market_id}", query)
    
    async def recall_venture_context(self, venture_id: str, query: str = "venture analysis") -> List[Dict[str, Any]]:
        """Retrieve previous venture analyses."""
        return await self.provider.recall(f"venture_{venture_id}", query)
    
    # ========== CHANGE DETECTION ==========
    
    async def compare_with_previous(self, market_id: str, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Compare current market state with previously stored state."""
        previous = await self.recall_market_context(market_id, "latest market state")
        
        if not previous:
            return {
                'has_previous': False,
                'changes': [],
                'summary': 'This is the first analysis for this market.'
            }
        
        # Get the most recent previous state
        prev_state = previous[0].get('metadata', {})
        
        changes = []
        
        # Compare key metrics
        comparisons = [
            ('competitor_count', 'Competitors'),
            ('average_price', 'Average Price'),
            ('demand_signal', 'Demand Signal'),
        ]
        
        for field, label in comparisons:
            prev_val = prev_state.get(field)
            curr_val = current_state.get(field)
            if prev_val is not None and curr_val is not None and prev_val != curr_val:
                change_type = 'increase' if curr_val > prev_val else 'decrease'
                changes.append({
                    'field': label,
                    'previous_value': prev_val,
                    'current_value': curr_val,
                    'change_type': change_type,
                    'timestamp': datetime.utcnow().isoformat(),
                    'significance': 'high' if abs(curr_val - prev_val) / max(prev_val, 1) > 0.1 else 'medium',
                })
        
        # Check for new locations
        prev_locations = set(prev_state.get('top_locations', []))
        curr_locations = set(current_state.get('top_locations', []))
        new_locations = curr_locations - prev_locations
        if new_locations:
            for loc in new_locations:
                changes.append({
                    'field': 'New Location',
                    'previous_value': 'Not tracked',
                    'current_value': loc,
                    'change_type': 'new',
                    'timestamp': datetime.utcnow().isoformat(),
                    'significance': 'medium',
                })
        
        summary_parts = []
        for c in changes:
            if c['change_type'] == 'increase':
                summary_parts.append(f"{c['field']}: {c['previous_value']} → {c['current_value']} (↑)")
            elif c['change_type'] == 'decrease':
                summary_parts.append(f"{c['field']}: {c['previous_value']} → {c['current_value']} (↓)")
            elif c['change_type'] == 'new':
                summary_parts.append(f"New {c['field']}: {c['current_value']}")
        
        return {
            'has_previous': True,
            'changes': changes,
            'summary': '; '.join(summary_parts) if summary_parts else 'No significant changes detected.',
            'previous_analysis_date': prev_state.get('timestamp', 'Unknown'),
            'current_analysis_date': datetime.utcnow().isoformat(),
        }
    
    async def generate_change_summary(self, market_id: str, current_state: Dict[str, Any]) -> str:
        """Generate a human-readable change summary using Hindsight reflect."""
        query = (
            f"What has changed in the market since the previous analysis? "
            f"Current state: competitors={current_state.get('competitor_count')}, "
            f"price={current_state.get('average_price')}, "
            f"demand={current_state.get('demand_signal')}"
        )
        return await self.provider.reflect(f"market_{market_id}", query)
''',
    'app/hindsight/change_detector.py': '''from typing import Any, Dict, List
from datetime import datetime

class ChangeDetector:
    """Detects and categorizes changes between market states."""
    
    @staticmethod
    def detect_changes(previous: Dict[str, Any], current: Dict[str, Any]) -> List[Dict[str, Any]]:
        changes = []
        
        # Numeric field comparisons
        numeric_fields = {
            'competitor_count': 'Competitors',
            'average_price': 'Average Market Price',
            'demand_index': 'Demand Signal',
            'customer_concentration': 'Customer Concentration',
            'cac_estimate': 'CAC Estimate',
        }
        
        for field, label in numeric_fields.items():
            prev = previous.get(field)
            curr = current.get(field)
            if prev is not None and curr is not None:
                if prev != curr:
                    pct_change = ((curr - prev) / max(abs(prev), 1)) * 100
                    changes.append({
                        'field': label,
                        'previous_value': prev,
                        'current_value': curr,
                        'change_type': 'increase' if curr > prev else 'decrease',
                        'percentage_change': round(pct_change, 1),
                        'significance': ChangeDetector._assess_significance(pct_change),
                        'timestamp': datetime.utcnow().isoformat(),
                    })
        
        # List field comparisons (locations, competitors)
        list_fields = {
            'locations': 'Location',
            'competitor_names': 'Competitor',
        }
        
        for field, label in list_fields.items():
            prev_set = set(previous.get(field, []))
            curr_set = set(current.get(field, []))
            
            for item in curr_set - prev_set:
                changes.append({
                    'field': f'New {label}',
                    'previous_value': 'Not present',
                    'current_value': item,
                    'change_type': 'new',
                    'significance': 'medium',
                    'timestamp': datetime.utcnow().isoformat(),
                })
            
            for item in prev_set - curr_set:
                changes.append({
                    'field': f'Removed {label}',
                    'previous_value': item,
                    'current_value': 'No longer tracked',
                    'change_type': 'removed',
                    'significance': 'low',
                    'timestamp': datetime.utcnow().isoformat(),
                })
        
        return changes
    
    @staticmethod
    def _assess_significance(pct_change: float) -> str:
        abs_change = abs(pct_change)
        if abs_change > 20:
            return 'high'
        elif abs_change > 10:
            return 'medium'
        return 'low'
''',
    'app/api/routes/analysis.py': '''from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class StartAnalysisRequest(BaseModel):
    category_id: str
    city_id: str
    subcategory_id: str

@router.post("/start")
async def start_analysis(req: StartAnalysisRequest):
    return {"success": True, "data": {"id": "m_123", "status": "started"}}

@router.get("/{id}")
async def get_analysis(id: str):
    return {"success": True, "data": {"id": id, "status": "completed"}}
''',
    'app/api/routes/markets.py': '''from fastapi import APIRouter

router = APIRouter()

@router.get("/{id}")
async def get_market(id: str):
    return {"success": True, "data": {"id": id, "city_id": "hyd", "category_id": "fashion", "subcategory_id": "footwear", "city_name": "Hyderabad", "category_name": "Fashion", "subcategory_name": "Footwear"}}

@router.get("/{id}/map")
async def get_map(id: str):
    return {"success": True, "data": {}}

@router.get("/{id}/trajectory")
async def get_trajectory(id: str):
    return {"success": True, "data": {}}

@router.get("/{id}/pulse")
async def get_pulse(id: str):
    return {"success": True, "data": {}}

@router.get("/{id}/competitors")
async def get_competitors(id: str):
    return {"success": True, "data": []}

@router.get("/{id}/customers")
async def get_customers(id: str):
    return {"success": True, "data": []}

@router.get("/{id}/gaps")
async def get_gaps(id: str):
    return {"success": True, "data": []}
''',
    'app/api/routes/ventures.py': '''from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class AnalyzeRequest(BaseModel):
    url: str
    market_id: str

@router.post("/analyze")
async def analyze_venture(req: AnalyzeRequest):
    return {"success": True, "data": {"id": "v_123"}}

@router.get("/{id}")
async def get_venture(id: str):
    return {"success": True, "data": {"id": id}}

@router.get("/{id}/xray")
async def get_xray(id: str):
    return {"success": True, "data": {}}
''',
    'app/api/routes/competitors.py': '''from fastapi import APIRouter

router = APIRouter()

@router.get("/{market_id}")
async def get_competitors_list(market_id: str):
    return {"success": True, "data": []}
''',
    'app/api/routes/simulation.py': '''from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class RunSimRequest(BaseModel):
    market_id: str

@router.post("/run")
async def run_simulation(req: RunSimRequest):
    return {"success": True, "data": {"id": "sim_123"}}

@router.get("/{id}")
async def get_simulation(id: str):
    return {"success": True, "data": {}}

@router.post("/what-if")
async def what_if_simulation():
    return {"success": True, "data": {}}
''',
    'app/api/routes/trajectory.py': '''from fastapi import APIRouter

router = APIRouter()

@router.get("/{market_id}")
async def get_trajectory(market_id: str):
    return {"success": True, "data": {}}
''',
    'app/api/routes/maps.py': '''from fastapi import APIRouter

router = APIRouter()

@router.get("/{market_id}/heatmap")
async def get_heatmap(market_id: str):
    return {"success": True, "data": {}}
''',
    'app/api/routes/customers.py': '''from fastapi import APIRouter

router = APIRouter()

@router.get("/{market_id}/segments")
async def get_customer_segments(market_id: str):
    return {"success": True, "data": []}
''',
    'app/api/routes/hindsight_routes.py': '''from fastapi import APIRouter

router = APIRouter()

@router.get("/{venture_id}/context")
async def get_context(venture_id: str):
    return {"success": True, "data": []}

@router.get("/{venture_id}/changes")
async def get_changes(venture_id: str):
    return {"success": True, "data": []}

@router.get("/{venture_id}/timeline")
async def get_timeline(venture_id: str):
    return {"success": True, "data": []}
'''
}

if not os.path.exists(base_dir):
    os.makedirs(base_dir)

for d in dirs:
    os.makedirs(os.path.join(base_dir, d), exist_ok=True)

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
