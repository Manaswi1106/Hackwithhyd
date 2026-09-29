from pydantic import BaseModel
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
