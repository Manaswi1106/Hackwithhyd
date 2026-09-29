from typing import Dict, List, Optional
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
