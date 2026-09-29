from typing import Dict, List, Optional, Tuple
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
