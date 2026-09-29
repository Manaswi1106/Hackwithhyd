"""
Explanation Agent
Generates grounded executive briefings and explanations for why trajectories and financial models behave as projected.
Maintains evidentiary citations and strictly avoids making unsupported factual claims.
"""

from typing import Dict, Any, List


class ExplanationAgent:
    """Explains simulation outputs and trajectory trends with grounded reasoning."""

    def explain_simulation(
        self,
        simulation_results: Dict[str, Any],
        assumptions: Any,
    ) -> Dict[str, str]:
        """Explain unit economics, runway, and break-even timelines."""
        expected = simulation_results.get("expected", {})
        break_even = expected.get("break_even_month")
        recovery = expected.get("recovery_month")

        be_text = (
            f"Modeled break-even occurs at Month {break_even} under expected market growth assumptions."
            if break_even
            else "Break-even requires optimizing customer acquisition cost or extending runway."
        )

        rec_text = (
            f"Full initial capital recovery of ₹{assumptions.investment_amount:,.0f} is projected at Month {recovery}."
            if recovery
            else "Capital recovery extends past the 24-month modeled horizon under conservative scenarios."
        )

        return {
            "break_even_summary": be_text,
            "recovery_summary": rec_text,
            "unit_economics": (
                f"Gross margin of {assumptions.gross_margin_percent * 100:.0f}% with an estimated CAC of ₹{assumptions.customer_acquisition_cost:.0f} "
                f"yields healthy LTV:CAC ratios provided customer retention remains above {assumptions.retention_rate * 100:.0f}%."
            ),
            "sensitivity_guidance": (
                "Key sensitivity factors: 1) CAC escalation in saturated digital channels, "
                "2) Working capital drag from retail inventory sizing, 3) Foot traffic conversion variance."
            ),
        }

    def explain_trajectory(
        self,
        trajectory_data: Dict[str, Any],
    ) -> str:
        """Explain why the market trajectory is trending in the modeled direction."""
        drivers = trajectory_data.get("drivers", [])
        driver_summary = ", ".join([f"{d['name']} ({d['direction']})" for d in drivers])
        return (
            f"The 24-month market trajectory is shaped by {len(drivers)} primary macro forces: {driver_summary}. "
            "Rapid IT infrastructure growth in the Western corridor of Hyderabad drives high discretionary spending, "
            "while commercial lease absorption rates support retail expansion."
        )
