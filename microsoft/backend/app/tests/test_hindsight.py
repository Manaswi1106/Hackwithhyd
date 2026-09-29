"""
Tests for Hindsight Memory Layer
Verifies retain, recall, reflect, and the core 'What Changed?' differential detection loop.
"""

import pytest
from app.hindsight.providers import MockHindsightProvider
from app.hindsight.memory_service import HindsightMemoryService
from app.hindsight.change_detector import ChangeDetector


@pytest.mark.asyncio
async def test_hindsight_retain_and_recall():
    """Verify storing market observations and retrieving them via semantic query."""
    provider = MockHindsightProvider()
    service = HindsightMemoryService(provider=provider, bank_id="test-bank")

    # Retain initial market observation
    mem_id = await service.remember_market_state(
        market_id="hyd-footwear",
        state={
            "competitor_count": 8,
            "average_price": 1799.0,
            "demand_signal": "high",
            "top_locations": ["Gachibowli", "Madhapur", "HITEC City"],
            "city": "Hyderabad",
            "category": "Fashion",
            "subcategory": "Footwear",
        }
    )

    assert mem_id.startswith("mock_mem_")

    # Recall the memory
    recalled = await service.recall_market_context("hyd-footwear", "market state")
    assert len(recalled) >= 1
    assert "Gachibowli" in recalled[0]["text"]
    assert "1799" in recalled[0]["text"]


@pytest.mark.asyncio
async def test_hindsight_change_detection_loop():
    """Verify the critical 'What Changed?' capability comparing analysis_001 with analysis_002."""
    provider = MockHindsightProvider()
    service = HindsightMemoryService(provider=provider, bank_id="test-bank")

    # Cycle 1: Store initial market state
    await service.remember_market_state(
        market_id="hyd-footwear",
        state={
            "competitor_count": 8,
            "average_price": 1799.0,
            "demand_signal": "high",
            "top_locations": ["Gachibowli", "Madhapur", "HITEC City"],
            "city": "Hyderabad",
            "category": "Fashion",
            "subcategory": "Footwear",
        }
    )

    # Cycle 2: Market has evolved — new competitors and price change
    evolved_state = {
        "competitor_count": 11,      # Changed: 8 -> 11
        "average_price": 1899.0,     # Changed: 1799 -> 1899
        "demand_signal": "high",
        "top_locations": ["Gachibowli", "Madhapur", "HITEC City", "Kondapur"],  # New location
        "city": "Hyderabad",
        "category": "Fashion",
        "subcategory": "Footwear",
    }

    comparison = await service.compare_with_previous(
        market_id="hyd-footwear",
        current_state=evolved_state,
    )

    assert comparison["has_previous"] is True
    changes = comparison["changes"]

    fields_changed = [c["field"] for c in changes]
    assert "Competitors" in fields_changed or "competitor_count" in str(changes)
    assert "Average Price" in fields_changed or "average_price" in str(changes)
    assert "New Location" in fields_changed or any("Kondapur" in str(c) for c in changes)


def test_deterministic_change_detector():
    """Verify change detector computes correct percentage changes and significance."""
    prev_state = {
        "competitor_count": 8,
        "average_price": 1799.0,
        "demand_index": 100.0,
        "locations": ["Gachibowli", "Madhapur"],
    }
    curr_state = {
        "competitor_count": 11,
        "average_price": 1899.0,
        "demand_index": 114.0,
        "locations": ["Gachibowli", "Madhapur", "Kondapur"],
    }

    changes = ChangeDetector.detect_changes(prev_state, curr_state)

    comp_change = next(c for c in changes if "Competitor" in c["field"])
    assert comp_change["previous_value"] == 8
    assert comp_change["current_value"] == 11
    assert comp_change["change_type"] == "increase"
    assert comp_change["percentage_change"] == 37.5

    loc_change = next(c for c in changes if "Location" in c["field"] and c["change_type"] == "new")
    assert loc_change["current_value"] == "Kondapur"
