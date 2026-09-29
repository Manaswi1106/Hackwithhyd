"""
Advanced What-If Simulation Engine
Authoritative backend calculations for location and venture feasibility.
The frontend NEVER calculates business metrics independently.

Inputs:
- Rent
- Store Size
- Marketing Budget
- Competitor Count
- Festival Season
- Metro Opening
- Inflation
- Customer Segment

Outputs:
- Monthly Revenue
- Expenses
- Profit
- Break-even Month
- Customer Growth
- Success Probability
- 12-month Forecast
- Profit Trend
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class WhatIfSimulationInputs(BaseModel):
    rent: float = Field(default=180000.0, description="Monthly commercial rent in INR")
    store_size: float = Field(default=1200.0, description="Store area in square feet")
    marketing_budget: float = Field(default=150000.0, description="Monthly marketing budget in INR")
    competitor_count: int = Field(default=14, description="Count of nearby direct competitors")
    festival_season: bool = Field(default=False, description="Whether festival seasonality is active")
    metro_opening: bool = Field(default=False, description="Whether direct metro access / new line is active")
    inflation: float = Field(default=5.0, description="Annual inflation percentage")
    customer_segment: str = Field(default="Tech Professionals", description="Primary target demographic")
    category: str = Field(default="Specialty Coffee", description="Retail venture category")
    locality: str = Field(default="Madhapur", description="Selected commercial locality")

class WhatIfSimulationEngine:
    """Calculates all venture performance metrics authoritatively on the backend."""

    SEGMENT_PARAMS = {
        "Tech Professionals": {"ticket_base": 420.0, "cac": 320.0, "freq": 3.2, "growth": 0.085},
        "Corporate Executives": {"ticket_base": 580.0, "cac": 450.0, "freq": 2.8, "growth": 0.075},
        "Students": {"ticket_base": 240.0, "cac": 180.0, "freq": 4.1, "growth": 0.110},
        "Families": {"ticket_base": 650.0, "cac": 380.0, "freq": 2.2, "growth": 0.065},
        "Luxury Buyers": {"ticket_base": 1200.0, "cac": 750.0, "freq": 1.8, "growth": 0.055},
        "Transit Commuters": {"ticket_base": 260.0, "cac": 200.0, "freq": 3.8, "growth": 0.090},
    }

    @classmethod
    def calculate(cls, inputs: WhatIfSimulationInputs) -> Dict[str, Any]:
        seg = cls.SEGMENT_PARAMS.get(inputs.customer_segment, cls.SEGMENT_PARAMS["Tech Professionals"])

        # Base price / ticket calculation
        inflation_factor = 1.0 + (inputs.inflation * 0.01)
        aov = seg["ticket_base"] * (1.0 + (inputs.inflation * 0.005))

        # Demand multipliers
        fest_mult = 1.25 if inputs.festival_season else 1.0
        metro_mult = 1.15 if inputs.metro_opening else 1.0
        comp_drag = max(0.65, 1.0 - (inputs.competitor_count * 0.012))
        inflation_demand_drag = max(0.85, 1.0 - (inputs.inflation * 0.01 * 0.35))

        # Base organic and marketing customers
        base_organic = (inputs.store_size * 1.8) # physical capacity factor
        marketing_customers = (inputs.marketing_budget / max(50.0, seg["cac"])) * 0.75
        
        effective_monthly_customers = (
            (base_organic + marketing_customers)
            * fest_mult
            * metro_mult
            * comp_drag
            * inflation_demand_drag
        )
        effective_monthly_customers = round(effective_monthly_customers)

        # Revenue
        monthly_revenue = effective_monthly_customers * aov * seg["freq"]

        # Expense breakdown
        cogs_rate = 0.38
        cogs = monthly_revenue * cogs_rate
        rent_expense = inputs.rent
        staff_cost = (inputs.store_size * 42.0) * inflation_factor
        marketing_expense = inputs.marketing_budget
        utilities_ops = (inputs.store_size * 28.0) * inflation_factor

        total_expenses = rent_expense + cogs + staff_cost + marketing_expense + utilities_ops
        monthly_profit = monthly_revenue - total_expenses

        # Initial Capex & Setup Investment
        capex = (inputs.store_size * 2200.0) + (total_expenses * 1.8)

        # 12-Month Projections & Break-even analysis
        forecast_12 = []
        profit_trend = []
        cumulative_cashflow = -capex
        break_even_month = None

        monthly_growth_rate = seg["growth"]

        for m in range(1, 13):
            # Gradual ramp-up during first 6 months
            ramp = min(1.0, 0.45 + (m * 0.09))
            m_cust = round(effective_monthly_customers * ramp * ((1.0 + monthly_growth_rate) ** (m - 1)))
            
            # Seasonal boost for months 10-12 (festive quarter)
            m_fest = 1.20 if (m in [10, 11, 12] or inputs.festival_season) else 1.0
            
            m_rev = round(m_cust * aov * seg["freq"] * m_fest)
            m_cogs = round(m_rev * cogs_rate)
            m_exp = round(rent_expense + m_cogs + staff_cost + marketing_expense + utilities_ops)
            m_prof = m_rev - m_exp

            cumulative_cashflow += m_prof
            if break_even_month is None and cumulative_cashflow >= 0:
                break_even_month = m

            forecast_12.append({
                "month": f"M{m}",
                "month_num": m,
                "revenue": m_rev,
                "expenses": m_exp,
                "profit": m_prof,
                "customers": m_cust,
                "cumulative_cashflow": round(cumulative_cashflow),
            })
            profit_trend.append(m_prof)

        # If not broken even in 12 months, project months 13-24
        if break_even_month is None:
            c_flow = cumulative_cashflow
            for m in range(13, 25):
                m_cust = round(effective_monthly_customers * ((1.0 + monthly_growth_rate) ** (m - 1)))
                m_rev = round(m_cust * aov * seg["freq"])
                m_exp = round(rent_expense + (m_rev * cogs_rate) + staff_cost + marketing_expense + utilities_ops)
                m_prof = m_rev - m_exp
                c_flow += m_prof
                if c_flow >= 0:
                    break_even_month = m
                    break

        if break_even_month is None:
            break_even_display = "> 24 months (High Capex / High Rent)"
            break_even_val = 25
        else:
            break_even_display = f"Month {break_even_month}"
            break_even_val = break_even_month

        # Success Probability Calculation (0 to 100%)
        margin_pct = (monthly_profit / max(1.0, monthly_revenue)) * 100
        rent_ratio = (rent_expense / max(1.0, monthly_revenue)) * 100

        score_components = 0.0
        # Positive margin bonus
        if margin_pct > 20:
            score_components += 40.0
        elif margin_pct > 10:
            score_components += 30.0
        elif margin_pct > 0:
            score_components += 15.0
        else:
            score_components += 0.0

        # Rent health (ideal < 18%)
        if rent_ratio < 15:
            score_components += 30.0
        elif rent_ratio < 22:
            score_components += 20.0
        elif rent_ratio < 30:
            score_components += 10.0
        else:
            score_components += 2.0

        # Competitor headroom
        if inputs.competitor_count <= 10:
            score_components += 20.0
        elif inputs.competitor_count <= 25:
            score_components += 12.0
        else:
            score_components += 5.0

        # Metro / Festival boost
        if inputs.metro_opening:
            score_components += 5.0
        if inputs.festival_season:
            score_components += 5.0

        success_prob = min(96.0, max(12.0, round(score_components, 1)))

        return {
            "inputs": inputs.model_dump(),
            "monthly_revenue": round(monthly_revenue),
            "expenses": round(total_expenses),
            "profit": round(monthly_profit),
            "break_even_month": break_even_display,
            "break_even_month_num": break_even_val,
            "customer_growth": f"+{round(monthly_growth_rate * 100, 1)}% MoM",
            "success_probability": success_prob,
            "expense_breakdown": {
                "rent": round(rent_expense),
                "cogs": round(cogs),
                "staff": round(staff_cost),
                "marketing": round(marketing_expense),
                "utilities": round(utilities_ops),
            },
            "metrics": {
                "profit_margin_pct": round(margin_pct, 1),
                "rent_to_revenue_pct": round(rent_ratio, 1),
                "monthly_customers": effective_monthly_customers,
                "average_order_value": round(aov),
                "estimated_capex": round(capex),
            },
            "total_expenses": round(total_expenses),
            "break_even_display": break_even_display,
            "forecast_12": forecast_12,
            "forecast_12_month": forecast_12,
            "profit_trend": profit_trend,
        }
