"""
Domain-Specific Recommendation Engine
Generates actionable, evidence-grounded recommendations based on
detected venture domain. Supports "Test this change" intervention loop.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
import uuid


@dataclass
class Recommendation:
    """A single actionable recommendation."""
    id: str
    title: str
    description: str
    domain: str  # Which domain this applies to
    category: str  # growth, retention, pricing, operations, marketing
    expected_impact: str  # e.g., "+12-18% conversion rate"
    effort: str  # low, medium, high
    evidence_basis: str  # observed, inferred, modeled
    simulation_params: Optional[Dict[str, float]] = None  # What to change in simulation
    rationale: str = ""  # Why this recommendation matters


@dataclass
class InterventionResult:
    """Before/after comparison when testing a recommendation."""
    recommendation_id: str
    recommendation_title: str
    before: Dict[str, Any] = field(default_factory=dict)
    after: Dict[str, Any] = field(default_factory=dict)
    impact_summary: str = ""
    confidence: str = "modeled"


# ---------------------------------------------------------------------------
# Domain-Specific Recommendation Templates
# ---------------------------------------------------------------------------

# Each template: (title, description, category, impact, effort, evidence, sim_params, rationale)

ECOMMERCE_RECOMMENDATIONS = [
    ("Implement student/youth discount program",
     "Offer 10-15% discount for students and young professionals (18-25) to capture the price-sensitive early-career segment.",
     "pricing", "+15-22% youth segment conversion", "low", "inferred",
     {"average_order_value_delta_pct": -0.12, "monthly_customers_delta_pct": 0.20},
     "Price-sensitive youth segments often have high social sharing potential, creating organic acquisition."),
    ("Launch referral/loyalty rewards program",
     "Implement a points-based loyalty program with referral bonuses to drive repeat purchases and organic acquisition.",
     "retention", "+25-35% repeat purchase rate", "medium", "modeled",
     {"retention_rate_delta": 0.12, "customer_acquisition_cost_delta_pct": -0.15},
     "Repeat customers have 60-70% lower acquisition cost and higher AOV than new customers."),
    ("Add 'try before you buy' or easy returns",
     "Implement a 14-day home trial or hassle-free returns policy to reduce purchase hesitation.",
     "growth", "+10-18% checkout completion", "medium", "modeled",
     {"monthly_customers_delta_pct": 0.14, "operating_cost_monthly_delta_pct": 0.05},
     "Return policies increase conversion by reducing risk perception, even though actual return rates are typically 8-15%."),
    ("Launch seasonal/festival collection drops",
     "Create limited-edition collections timed with major festivals and seasons to drive urgency and social buzz.",
     "marketing", "+20-30% seasonal revenue spike", "high", "modeled",
     {"average_order_value_delta_pct": 0.15, "marketing_budget_monthly_delta_pct": 0.20},
     "Limited drops create urgency and social sharing, dramatically increasing reach during key buying seasons."),
    ("Expand to marketplace channels (Amazon/Flipkart)",
     "List products on major marketplaces to capture high-intent traffic without incremental ad spend.",
     "growth", "+30-45% total addressable customers", "high", "inferred",
     {"monthly_customers_delta_pct": 0.35, "gross_margin_percent_delta": -0.08},
     "Marketplaces provide built-in traffic but charge 15-25% commission, compressing margins."),
]

SAAS_RECOMMENDATIONS = [
    ("Implement freemium tier or extended free trial",
     "Offer a feature-limited free plan or 30-day trial to lower the barrier to entry and build a self-serve pipeline.",
     "growth", "+40-60% signup volume", "medium", "modeled",
     {"monthly_customers_delta_pct": 0.50, "average_order_value_delta_pct": -0.25},
     "Freemium models increase top-of-funnel volume; ~5% convert to paid within 90 days."),
    ("Launch annual billing discount (20% off)",
     "Offer a 20% discount for annual prepayment to improve cash flow and reduce churn.",
     "retention", "+30% annual commitment rate, -40% churn", "low", "modeled",
     {"retention_rate_delta": 0.15, "average_order_value_delta_pct": -0.03},
     "Annual subscribers have 3-5x lower churn than monthly subscribers."),
    ("Build self-serve onboarding with product tours",
     "Implement guided product tours and onboarding checklists to reduce time-to-value.",
     "retention", "+20-35% activation rate", "high", "modeled",
     {"retention_rate_delta": 0.10, "customer_acquisition_cost_delta_pct": -0.10},
     "Users who complete onboarding within 7 days have 2-3x higher retention."),
    ("Launch content marketing & SEO program",
     "Publish educational content targeting high-intent search queries to build organic acquisition pipeline.",
     "marketing", "+25-40% organic traffic in 6 months", "high", "modeled",
     {"marketing_budget_monthly_delta_pct": 0.15, "customer_acquisition_cost_delta_pct": -0.20},
     "Organic acquisition has 5-8x lower CAC than paid channels, compounding over time."),
    ("Add usage-based or per-seat pricing tier",
     "Introduce flexible pricing that scales with customer usage or team size.",
     "pricing", "+15-25% expansion revenue", "medium", "inferred",
     {"average_order_value_delta_pct": 0.18},
     "Usage-based pricing captures more value from power users without raising entry price."),
]

RESTAURANT_RECOMMENDATIONS = [
    ("Launch online ordering & delivery integration",
     "Integrate with delivery platforms or build own ordering system to capture takeout/delivery demand.",
     "growth", "+25-40% revenue from delivery channel", "medium", "modeled",
     {"monthly_customers_delta_pct": 0.30, "gross_margin_percent_delta": -0.05},
     "Delivery represents 30-40% of restaurant revenue post-pandemic."),
    ("Implement loyalty/rewards program for regulars",
     "Create a stamp card or points program that rewards repeat visits with free items or discounts.",
     "retention", "+20-30% repeat visit frequency", "low", "modeled",
     {"retention_rate_delta": 0.15, "average_order_value_delta_pct": 0.05},
     "Regular customers spend 67% more than new customers on average."),
    ("Host themed nights or special events",
     "Weekly themed events (live music, trivia, tasting nights) to drive traffic on slower days.",
     "marketing", "+15-25% weekday traffic", "low", "inferred",
     {"monthly_customers_delta_pct": 0.15, "marketing_budget_monthly_delta_pct": 0.08},
     "Events create social media content and word-of-mouth, filling capacity on traditionally slow nights."),
    ("Optimize menu pricing and engineering",
     "Analyze menu item profitability and redesign menu layout to highlight high-margin items.",
     "pricing", "+8-15% average check size", "low", "modeled",
     {"average_order_value_delta_pct": 0.12, "gross_margin_percent_delta": 0.03},
     "Strategic menu engineering can increase profitability by 10-15% without raising prices."),
    ("Launch catering and group ordering",
     "Offer catering packages for corporate events, parties, and large group orders.",
     "growth", "+20-30% B2B revenue stream", "medium", "modeled",
     {"monthly_customers_delta_pct": 0.15, "average_order_value_delta_pct": 0.40},
     "Catering orders are 5-10x average individual orders with lower per-unit prep costs."),
]

HEALTHCARE_RECOMMENDATIONS = [
    ("Implement telemedicine consultations",
     "Offer virtual consultations for follow-ups and minor concerns to expand capacity without physical infrastructure.",
     "growth", "+30-45% patient capacity", "medium", "modeled",
     {"monthly_customers_delta_pct": 0.35, "operating_cost_monthly_delta_pct": -0.10},
     "Telehealth reduces no-shows by 50% and enables serving patients beyond geographic limits."),
    ("Launch patient loyalty and wellness program",
     "Create annual wellness packages and health check-up bundles to drive repeat visits.",
     "retention", "+25-35% patient retention", "medium", "inferred",
     {"retention_rate_delta": 0.15, "average_order_value_delta_pct": 0.10},
     "Preventive health packages ensure regular touchpoints and early issue detection."),
    ("Implement online booking and queue management",
     "Allow patients to book slots online and view real-time wait times.",
     "operations", "-30% patient wait time, +15% satisfaction", "medium", "modeled",
     {"monthly_customers_delta_pct": 0.12, "operating_cost_monthly_delta_pct": -0.05},
     "Online booking reduces phone staff load and allows better capacity planning."),
    ("Launch health content marketing",
     "Publish educational health articles and videos to build trust and organic patient acquisition.",
     "marketing", "+20-30% organic patient inquiries", "low", "modeled",
     {"customer_acquisition_cost_delta_pct": -0.20, "monthly_customers_delta_pct": 0.15},
     "Health content builds authority and trust, key factors in healthcare provider selection."),
]

EDUCATION_RECOMMENDATIONS = [
    ("Offer free introductory course or trial class",
     "Provide a free mini-course or sample class to demonstrate teaching quality and build trust.",
     "growth", "+35-50% enrollment conversion", "low", "modeled",
     {"monthly_customers_delta_pct": 0.40, "average_order_value_delta_pct": -0.05},
     "Free trials let students experience the quality before committing to full program fees."),
    ("Launch placement assistance or career support",
     "Add career counseling, resume workshops, and placement partnerships to improve outcomes.",
     "retention", "+20-30% completion rate, higher referrals", "high", "inferred",
     {"retention_rate_delta": 0.15, "average_order_value_delta_pct": 0.10},
     "Career outcomes are the #1 factor students consider; strong outcomes drive word-of-mouth."),
    ("Implement flexible payment plans (EMI)",
     "Offer 3-6 month installment plans to make programs accessible to price-sensitive students.",
     "pricing", "+20-30% enrollment from price-sensitive segment", "low", "modeled",
     {"monthly_customers_delta_pct": 0.25, "average_order_value_delta_pct": -0.03},
     "EMI options expand the addressable market by 2-3x without discounting the total price."),
]

FINANCE_RECOMMENDATIONS = [
    ("Simplify onboarding with KYC automation",
     "Implement AI-powered document verification and auto-fill to reduce onboarding friction from 20min to 5min.",
     "growth", "+25-40% onboarding completion", "high", "modeled",
     {"monthly_customers_delta_pct": 0.30, "operating_cost_monthly_delta_pct": -0.10},
     "Every additional step in onboarding loses 15-20% of potential customers."),
    ("Launch financial literacy content hub",
     "Create educational content about personal finance, investing, and insurance to build trust and organic acquisition.",
     "marketing", "+20-30% organic lead generation", "medium", "modeled",
     {"customer_acquisition_cost_delta_pct": -0.25, "monthly_customers_delta_pct": 0.20},
     "Trust is the primary barrier in financial services; education-first marketing builds long-term pipelines."),
    ("Implement referral bonus program",
     "Offer cash rewards or fee waivers for successful referrals.",
     "growth", "+15-25% new customer acquisition", "low", "modeled",
     {"monthly_customers_delta_pct": 0.20, "customer_acquisition_cost_delta_pct": -0.15},
     "Referred financial customers have 2x higher lifetime value and lower churn."),
]

GENERIC_RECOMMENDATIONS = [
    ("Optimize digital presence and SEO",
     "Improve website loading speed, mobile responsiveness, and search engine visibility to increase organic traffic.",
     "marketing", "+15-25% organic traffic", "medium", "modeled",
     {"customer_acquisition_cost_delta_pct": -0.15, "monthly_customers_delta_pct": 0.15},
     "Organic search is the most cost-effective long-term customer acquisition channel."),
    ("Implement customer feedback loop",
     "Set up systematic collection and response to customer feedback to improve satisfaction and retention.",
     "retention", "+10-20% customer satisfaction", "low", "inferred",
     {"retention_rate_delta": 0.08},
     "Companies that act on feedback see 25% higher retention rates."),
    ("Launch social media marketing campaign",
     "Build active presence on relevant social platforms to increase brand awareness and engagement.",
     "marketing", "+20-30% brand awareness", "medium", "modeled",
     {"marketing_budget_monthly_delta_pct": 0.15, "monthly_customers_delta_pct": 0.15},
     "Social media enables direct customer engagement and organic content distribution."),
    ("Develop strategic partnerships",
     "Form alliances with complementary businesses to cross-promote and expand reach.",
     "growth", "+15-25% customer reach", "medium", "inferred",
     {"monthly_customers_delta_pct": 0.18, "customer_acquisition_cost_delta_pct": -0.10},
     "Partnerships provide access to established audiences at lower cost than direct acquisition."),
]

# Map domain IDs to recommendation templates
DOMAIN_RECOMMENDATIONS: Dict[str, list] = {
    "ecommerce": ECOMMERCE_RECOMMENDATIONS,
    "technology": SAAS_RECOMMENDATIONS,
    "food_beverage": RESTAURANT_RECOMMENDATIONS,
    "healthcare": HEALTHCARE_RECOMMENDATIONS,
    "education": EDUCATION_RECOMMENDATIONS,
    "finance": FINANCE_RECOMMENDATIONS,
}


class RecommendationEngine:
    """Generates domain-specific recommendations and intervention simulations."""
    
    def generate_recommendations(
        self,
        domain: str,
        sub_domain: str = "",
        evidence: Optional[Dict[str, Any]] = None,
        max_recommendations: int = 5,
    ) -> List[Dict[str, Any]]:
        """Generate recommendations for the detected domain."""
        templates = DOMAIN_RECOMMENDATIONS.get(domain, GENERIC_RECOMMENDATIONS)
        
        # If domain has specific templates, mix in 1-2 generic ones
        if domain in DOMAIN_RECOMMENDATIONS and len(templates) < max_recommendations:
            templates = templates + GENERIC_RECOMMENDATIONS[:max_recommendations - len(templates)]
        elif domain not in DOMAIN_RECOMMENDATIONS:
            templates = GENERIC_RECOMMENDATIONS
        
        recommendations = []
        for i, (title, desc, category, impact, effort, evidence_basis, sim_params, rationale) in enumerate(templates[:max_recommendations]):
            rec = Recommendation(
                id=f"rec_{domain}_{i+1}",
                title=title,
                description=desc,
                domain=domain,
                category=category,
                expected_impact=impact,
                effort=effort,
                evidence_basis=evidence_basis,
                simulation_params=sim_params,
                rationale=rationale,
            )
            recommendations.append(asdict(rec))
        
        return recommendations
    
    def compute_intervention(
        self,
        recommendation: Dict[str, Any],
        current_assumptions: Dict[str, float],
    ) -> Dict[str, Any]:
        """Compute before/after simulation parameters for testing a recommendation."""
        sim_params = recommendation.get("simulation_params") or recommendation.get("intervention_parameters") or {}
        if not sim_params:

            return {
                "recommendation_id": recommendation.get("id", ""),
                "recommendation_title": recommendation.get("title", ""),
                "modified_assumptions": current_assumptions,
                "changes_applied": [],
            }
        
        modified = dict(current_assumptions)
        changes_applied = []
        
        for param_key, delta in sim_params.items():
            if param_key.endswith("_delta_pct"):
                # Percentage delta
                base_key = param_key.replace("_delta_pct", "")
                if base_key in modified:
                    old_val = modified[base_key]
                    new_val = old_val * (1 + delta)
                    modified[base_key] = round(new_val, 2)
                    changes_applied.append({
                        "parameter": base_key,
                        "old_value": old_val,
                        "new_value": round(new_val, 2),
                        "change_type": "percentage",
                        "delta": f"{delta*100:+.0f}%",
                    })
            elif param_key.endswith("_delta"):
                # Absolute delta
                base_key = param_key.replace("_delta", "")
                if base_key in modified:
                    old_val = modified[base_key]
                    new_val = old_val + delta
                    modified[base_key] = round(new_val, 2)
                    changes_applied.append({
                        "parameter": base_key,
                        "old_value": old_val,
                        "new_value": round(new_val, 2),
                        "change_type": "absolute",
                        "delta": f"{delta:+.2f}",
                    })
        
        return {
            "recommendation_id": recommendation.get("id", ""),
            "recommendation_title": recommendation.get("title", ""),
            "modified_assumptions": modified,
            "changes_applied": changes_applied,
        }
