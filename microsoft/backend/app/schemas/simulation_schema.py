from pydantic import BaseModel
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
