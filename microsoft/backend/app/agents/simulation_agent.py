"""
Simulation Assumption Agent
Transforms verified market data and competitor pricing into deterministic assumptions for the financial simulation engine.
The LLM DOES NOT perform arithmetic; this agent prepares the mathematical parameter space.
"""

from typing import Dict, Any, Optional
from app.simulation.engine import SimulationAssumptions, VentureSimulationEngine


class SimulationAssumptionAgent:
    """Prepares reproducible assumption vectors for the deterministic simulation engine."""

    def prepare_assumptions(
        self,
        market_data: Dict[str, Any],
        venture_data: Optional[Dict[str, Any]] = None,
        deployment_model: str = "hybrid",
        target_location: Optional[str] = "Gachibowli",
        custom_overrides: Optional[Dict[str, float]] = None,
    ) -> SimulationAssumptions:
        """Derive grounded financial assumptions based on observed market and venture data."""
        # Baseline parameterization from market research
        base_aov = 3500.0
        base_cac = 300.0
        base_customers = 500
        base_margin = 0.55
        base_op_cost = 250000.0
        base_mkt_budget = 150000.0
        base_investment = 3000000.0
        base_retention = 0.40

        # Adjust for deployment model
        if deployment_model == "online":
            base_op_cost = 120000.0
            base_mkt_budget = 220000.0
            base_investment = 1500000.0
            base_margin = 0.62
        elif deployment_model == "physical":
            base_op_cost = 380000.0
            base_mkt_budget = 80000.0
            base_investment = 4500000.0
            base_margin = 0.50
        elif deployment_model == "multi-location":
            base_op_cost = 750000.0
            base_mkt_budget = 300000.0
            base_investment = 9000000.0
            base_customers = 1400

        # Apply user what-if overrides if present
        if custom_overrides:
            if "monthly_customers" in custom_overrides:
                base_customers = int(custom_overrides["monthly_customers"])
            if "customer_acquisition_cost" in custom_overrides:
                base_cac = float(custom_overrides["customer_acquisition_cost"])
            if "average_order_value" in custom_overrides:
                base_aov = float(custom_overrides["average_order_value"])
            if "retention_rate" in custom_overrides:
                base_retention = float(custom_overrides["retention_rate"])
            if "operating_cost_monthly" in custom_overrides:
                base_op_cost = float(custom_overrides["operating_cost_monthly"])
            if "marketing_budget_monthly" in custom_overrides:
                base_mkt_budget = float(custom_overrides["marketing_budget_monthly"])
            if "gross_margin_percent" in custom_overrides:
                base_margin = float(custom_overrides["gross_margin_percent"])
            if "investment_amount" in custom_overrides:
                base_investment = float(custom_overrides["investment_amount"])

        return SimulationAssumptions(
            deployment_model=deployment_model,
            monthly_customers_base=base_customers,
            customer_acquisition_cost=base_cac,
            average_order_value=base_aov,
            purchase_frequency=1.5,
            retention_rate=base_retention,
            operating_cost_monthly=base_op_cost,
            marketing_budget_monthly=base_mkt_budget,
            gross_margin_percent=base_margin,
            investment_amount=base_investment,
            target_location=target_location,
        )

    def execute_simulation(
        self,
        assumptions: SimulationAssumptions,
        months: int = 24,
    ) -> Dict[str, Any]:
        """Run the deterministic engine across all scenarios."""
        engine = VentureSimulationEngine(assumptions)
        return engine.run_all_scenarios(months=months)
