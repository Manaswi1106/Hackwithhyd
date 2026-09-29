from pydantic import BaseModel, HttpUrl
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
