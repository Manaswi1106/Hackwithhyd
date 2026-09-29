from pydantic import BaseModel
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
