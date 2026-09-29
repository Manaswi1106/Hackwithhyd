from pydantic import BaseModel
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
