"""
Hindsight Memory Service for VentureScope

This is the central memory service that stores and retrieves market intelligence
using Hindsight by Vectorize. It provides high-level domain-specific operations
on top of the raw Hindsight retain/recall/reflect primitives.

Bank naming convention:
    - market_{market_id}     — Market-level observations (competitors, pricing, demand)
    - venture_{venture_id}   — Venture-specific analysis and simulation results
    - global_intelligence    — Cross-market insights and patterns

Tags are used for fine-grained filtering:
    - type:market_state, type:competitor, type:customer, type:simulation
    - market:{market_id}
    - venture:{venture_id}
    - city:{city_id}
    - category:{category_id}
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from .providers import HindsightProvider
from .change_detector import ChangeDetector
import json
import logging

logger = logging.getLogger(__name__)

# Default bank for all VentureScope market intelligence
DEFAULT_BANK_ID = "venturescope-market-intelligence"


class HindsightMemoryService:
    """Central memory service for the VentureScope platform.

    Stores and retrieves market intelligence using Hindsight.
    This is NOT a simple database wrapper — it's a semantic memory system
    that understands market context and can detect changes over time.
    """

    def __init__(self, provider: HindsightProvider, bank_id: str = DEFAULT_BANK_ID):
        self.provider = provider
        self.bank_id = bank_id
        self.change_detector = ChangeDetector()

    # ========== RETAIN OPERATIONS (Store Market Knowledge) ==========

    async def remember_market_state(
        self,
        market_id: str,
        state: Dict[str, Any],
        analysis_id: Optional[str] = None,
    ) -> str:
        """Store a complete market state observation.

        This is the primary memory operation — called after each analysis run.
        Stores the current snapshot of market conditions for future comparison.
        """
        content = (
            f"Market state analysis for {state.get('category', 'unknown')} / "
            f"{state.get('subcategory', 'unknown')} in {state.get('city', 'unknown')}. "
            f"Tracked competitors: {state.get('competitor_count', 'unknown')}. "
            f"Average market price: ₹{state.get('average_price', 'unknown')}. "
            f"Demand signal: {state.get('demand_signal', 'unknown')}. "
            f"Market growth: {state.get('growth_signal', 'unknown')}. "
            f"Customer concentration index: {state.get('customer_concentration', 'unknown')}. "
            f"Top locations by opportunity: {', '.join(state.get('top_locations', []))}. "
            f"Key customer segments: {', '.join(state.get('customer_segments', []))}."
        )

        tags = [
            "type:market_state",
            f"market:{market_id}",
            f"city:{state.get('city_id', 'unknown')}",
            f"category:{state.get('category_id', 'unknown')}",
        ]
        if analysis_id:
            tags.append(f"analysis:{analysis_id}")

        context = (
            f"Market intelligence analysis run. "
            f"Analysis ID: {analysis_id or 'initial'}. "
            f"City: {state.get('city', 'Hyderabad')}. "
            f"Category: {state.get('category', '')} > {state.get('subcategory', '')}."
        )

        return await self.provider.retain(
            bank_id=self.bank_id,
            content=content,
            context=context,
            tags=tags,
            occurred_at=datetime.now(timezone.utc).isoformat(),
            document_id=f"market_state_{market_id}_{analysis_id or 'initial'}",
            retain_mission=(
                "Extract and remember: competitor count, average price, demand signal, "
                "growth direction, top locations, customer segments, and any market changes. "
                "Focus on quantitative metrics that can be compared across time periods."
            ),
        )

    async def remember_competitor(
        self,
        market_id: str,
        competitor: Dict[str, Any],
    ) -> str:
        """Store a competitor observation."""
        content = (
            f"Competitor in {competitor.get('category', 'unknown')} market: "
            f"{competitor.get('name', 'unknown')}. "
            f"Price range: ₹{competitor.get('price_min', '?')} - ₹{competitor.get('price_max', '?')}. "
            f"Positioning: {competitor.get('positioning', 'unknown')}. "
            f"Locations: {', '.join(competitor.get('locations', []))}. "
            f"Target audience: {', '.join(competitor.get('target_audience', []))}. "
            f"Popular products: {', '.join(competitor.get('popular_products', []))}."
        )

        tags = [
            "type:competitor",
            f"market:{market_id}",
            f"competitor:{competitor.get('name', 'unknown').lower().replace(' ', '_')}",
        ]

        return await self.provider.retain(
            bank_id=self.bank_id,
            content=content,
            tags=tags,
            occurred_at=datetime.now(timezone.utc).isoformat(),
            retain_mission="Extract competitor name, pricing, positioning, locations, and target audience.",
        )

    async def remember_customer_insight(
        self,
        market_id: str,
        insight: Dict[str, Any],
    ) -> str:
        """Store a customer segment insight."""
        content = (
            f"Customer segment in market: {insight.get('segment_name', 'unknown')}. "
            f"Demand signal: {insight.get('demand_signal', 'unknown')}. "
            f"Typical spend: ₹{insight.get('typical_spend', 'unknown')}. "
            f"Price sensitivity: {insight.get('price_sensitivity', 'unknown')}. "
            f"Purchase frequency: {insight.get('purchase_frequency', 'unknown')}. "
            f"Key motivations: {', '.join(insight.get('motivations', []))}. "
            f"Key objections: {', '.join(insight.get('objections', []))}."
        )

        tags = [
            "type:customer",
            f"market:{market_id}",
            f"segment:{insight.get('segment_name', 'unknown').lower().replace(' ', '_')}",
        ]

        return await self.provider.retain(
            bank_id=self.bank_id,
            content=content,
            tags=tags,
            occurred_at=datetime.now(timezone.utc).isoformat(),
        )

    async def remember_venture_analysis(
        self,
        venture_id: str,
        analysis: Dict[str, Any],
    ) -> str:
        """Store a venture analysis result."""
        content = (
            f"Venture analysis for: {analysis.get('name', 'unknown')}. "
            f"URL: {analysis.get('url', 'N/A')}. "
            f"Business model: {analysis.get('business_model', 'unknown')}. "
            f"Price point: {analysis.get('price', 'unknown')}. "
            f"Positioning: {analysis.get('positioning', 'unknown')}. "
            f"Target audience: {analysis.get('target_audience', 'unknown')}. "
            f"Differentiators: {', '.join(analysis.get('differentiators', []))}. "
            f"Competitive overlap with: {', '.join(analysis.get('competitive_overlap', []))}. "
            f"Strength signals: {', '.join(analysis.get('strengths', []))}. "
            f"Risk signals: {', '.join(analysis.get('risks', []))}."
        )

        tags = [
            "type:venture_analysis",
            f"venture:{venture_id}",
        ]

        return await self.provider.retain(
            bank_id=self.bank_id,
            content=content,
            tags=tags,
            occurred_at=datetime.now(timezone.utc).isoformat(),
            document_id=f"venture_analysis_{venture_id}",
            retain_mission=(
                "Extract venture business model, pricing, positioning, target audience, "
                "differentiators, competitive overlap, strengths, and risks."
            ),
        )

    async def remember_simulation(
        self,
        venture_id: str,
        market_id: str,
        simulation: Dict[str, Any],
    ) -> str:
        """Store simulation results and assumptions."""
        expected = simulation.get("expected", {})
        content = (
            f"Simulation for venture {venture_id} in market {market_id}. "
            f"Deployment model: {simulation.get('deployment_model', 'unknown')}. "
            f"Expected break-even: month {expected.get('break_even_month', 'N/A')}. "
            f"Expected month-12 revenue: ₹{expected.get('revenue_month_12', 'N/A')}. "
            f"Expected month-12 customers: {expected.get('customers_month_12', 'N/A')}. "
            f"Investment required: ₹{simulation.get('investment_amount', 'N/A')}. "
            f"CAC assumption: ₹{simulation.get('cac', 'N/A')}. "
            f"AOV assumption: ₹{simulation.get('aov', 'N/A')}. "
            f"Retention assumption: {simulation.get('retention_rate', 'N/A')}."
        )

        tags = [
            "type:simulation",
            f"venture:{venture_id}",
            f"market:{market_id}",
        ]

        return await self.provider.retain(
            bank_id=self.bank_id,
            content=content,
            tags=tags,
            occurred_at=datetime.now(timezone.utc).isoformat(),
            retain_mission=(
                "Extract simulation assumptions (CAC, AOV, retention, investment) "
                "and results (break-even month, revenue projections, customer counts)."
            ),
        )

    # ========== RECALL OPERATIONS (Retrieve Market Knowledge) ==========

    async def recall_market_context(
        self,
        market_id: str,
        query: str = "What is the current market state?",
    ) -> List[Dict[str, Any]]:
        """Retrieve previous market observations."""
        return await self.provider.recall(
            bank_id=self.bank_id,
            query=query,
            tags=[f"market:{market_id}"],
            types=["world", "observation"],
            prefer_observations=True,
            max_tokens=2000,
        )

    async def recall_venture_context(
        self,
        venture_id: str,
        query: str = "What was the previous venture analysis?",
    ) -> List[Dict[str, Any]]:
        """Retrieve previous venture analyses."""
        return await self.provider.recall(
            bank_id=self.bank_id,
            query=query,
            tags=[f"venture:{venture_id}"],
            prefer_observations=True,
        )

    async def recall_competitors(
        self,
        market_id: str,
    ) -> List[Dict[str, Any]]:
        """Retrieve remembered competitor information."""
        return await self.provider.recall(
            bank_id=self.bank_id,
            query="What competitors exist in this market? Names, prices, positioning.",
            tags=[f"market:{market_id}", "type:competitor"],
            prefer_observations=True,
        )

    async def recall_simulation_history(
        self,
        venture_id: str,
    ) -> List[Dict[str, Any]]:
        """Retrieve previous simulation results."""
        return await self.provider.recall(
            bank_id=self.bank_id,
            query="What were the previous simulation results and assumptions?",
            tags=[f"venture:{venture_id}", "type:simulation"],
        )

    # ========== REFLECT OPERATIONS (Synthesized Intelligence) ==========

    async def reflect_on_market(
        self,
        market_id: str,
        question: str,
    ) -> Dict[str, Any]:
        """Get a synthesized reflection about the market with citations."""
        return await self.provider.reflect(
            bank_id=self.bank_id,
            query=question,
            budget="mid",
            tags=[f"market:{market_id}"],
        )

    async def reflect_on_venture(
        self,
        venture_id: str,
        question: str,
    ) -> Dict[str, Any]:
        """Get a synthesized reflection about a venture."""
        return await self.provider.reflect(
            bank_id=self.bank_id,
            query=question,
            budget="mid",
            tags=[f"venture:{venture_id}"],
        )

    # ========== CHANGE DETECTION (The Key Hindsight Feature) ==========

    async def compare_with_previous(
        self,
        market_id: str,
        current_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Compare current market state with previously stored state.

        This is the CORE Hindsight feature — "What Changed?"

        Returns detected changes with significance levels.
        """
        # Recall previous market state from Hindsight
        previous_memories = await self.recall_market_context(
            market_id,
            query="Latest market state: competitor count, average price, demand signal, locations",
        )

        if not previous_memories:
            return {
                "has_previous": False,
                "changes": [],
                "summary": "This is the first analysis for this market. "
                           "Future analyses will show what changed.",
                "previous_analysis_date": None,
                "current_analysis_date": datetime.now(timezone.utc).isoformat(),
            }

        # Extract previous state from recalled memory
        prev_memory = previous_memories[0]
        prev_text = prev_memory.get("text", "")

        # Use reflect to generate a detailed comparison
        reflect_result = await self.provider.reflect(
            bank_id=self.bank_id,
            query=(
                f"Compare the previous market state with the current state. "
                f"Current state: "
                f"competitors={current_state.get('competitor_count')}, "
                f"average_price=₹{current_state.get('average_price')}, "
                f"demand_signal={current_state.get('demand_signal')}, "
                f"locations={', '.join(current_state.get('top_locations', []))}. "
                f"What has changed? Be specific about numbers."
            ),
            budget="mid",
            tags=[f"market:{market_id}", "type:market_state"],
        )

        # Also use deterministic change detection
        changes = self.change_detector.detect_changes(
            previous=self._extract_metrics_from_text(prev_text),
            current=current_state,
        )

        summary_parts = []
        for c in changes:
            if c["change_type"] == "increase":
                summary_parts.append(
                    f"{c['field']}: {c['previous_value']} → {c['current_value']} (↑{c.get('percentage_change', '')}%)"
                )
            elif c["change_type"] == "decrease":
                summary_parts.append(
                    f"{c['field']}: {c['previous_value']} → {c['current_value']} (↓{abs(c.get('percentage_change', 0))}%)"
                )
            elif c["change_type"] == "new":
                summary_parts.append(f"New {c['field']}: {c['current_value']}")

        return {
            "has_previous": True,
            "changes": changes,
            "summary": "; ".join(summary_parts) if summary_parts else "No significant changes detected.",
            "reflect_summary": reflect_result.get("text", ""),
            "citations": reflect_result.get("citations", []),
            "previous_analysis_date": prev_memory.get("occurred_at", "Unknown"),
            "current_analysis_date": datetime.now(timezone.utc).isoformat(),
        }

    def _extract_metrics_from_text(self, text: str) -> Dict[str, Any]:
        """Extract numeric metrics from a recalled memory text.

        This is a simple extraction for change detection.
        In production, structured metadata from Hindsight observations
        would be used directly.
        """
        import re

        metrics: Dict[str, Any] = {}

        # Extract competitor count
        match = re.search(r'competitors?:?\s*(\d+)', text, re.IGNORECASE)
        if match:
            metrics["competitor_count"] = int(match.group(1))

        # Extract average price
        match = re.search(r'(?:average|avg)?\s*(?:market\s+)?price:?\s*₹?\s*([\d,]+)', text, re.IGNORECASE)
        if match:
            metrics["average_price"] = float(match.group(1).replace(",", ""))

        # Extract demand signal
        match = re.search(r'demand\s*(?:signal)?:?\s*(high|medium|low|\d+)', text, re.IGNORECASE)
        if match:
            metrics["demand_signal"] = match.group(1)

        # Extract top locations
        loc_match = re.search(r'Top locations(?: by opportunity)?:?\s*([^\.]+)', text, re.IGNORECASE)
        if loc_match:
            locs = [l.strip() for l in loc_match.group(1).split(",") if l.strip()]
            metrics["top_locations"] = locs
            metrics["locations"] = locs

        return metrics

    async def generate_change_summary(
        self,
        market_id: str,
        current_state: Dict[str, Any],
    ) -> str:
        """Generate a human-readable change summary using Hindsight reflect."""
        result = await self.reflect_on_market(
            market_id,
            question=(
                f"What has changed in this market since the last analysis? "
                f"Current state: competitors={current_state.get('competitor_count')}, "
                f"price=₹{current_state.get('average_price')}, "
                f"demand={current_state.get('demand_signal')}. "
                f"Summarize the key changes concisely."
            ),
        )
        return result.get("text", "Unable to generate change summary.")
