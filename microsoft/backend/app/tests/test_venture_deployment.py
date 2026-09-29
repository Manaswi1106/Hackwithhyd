"""
Tests for Upgraded Venture Deployment Simulation Pipeline
Covers:
1. SSRF URL Safety Validation
2. Multi-Signal Venture Classification across Domains (Fashion, Tech, Food, Health, EdTech)
3. Category Mismatch Detection
4. Domain-Specific Recommendation Engine & Intervention Deltas
5. Dynamic 500-Person Synthetic Population across Domains
6. Broken URL / Insufficient Evidence Graceful Handling
7. Full VentureAnalysisAgent Pipeline Integration
"""

import pytest
from app.agents.website_crawler import _is_private_ip, _validate_url_safety, _extract_page_evidence
from app.agents.venture_classifier import VentureClassifier
from app.agents.recommendation_engine import RecommendationEngine
from app.simulation.dynamic_population import DynamicPopulationGenerator
from app.agents.venture_agent import VentureAnalysisAgent


# ── 1. SSRF Protection Tests ────────────────────────────────────────────────

def test_ssrf_blocks_private_ips():
    """Verify SSRF protection flags private and cloud metadata IPs."""
    assert _is_private_ip("127.0.0.1") is True
    assert _is_private_ip("10.0.0.1") is True
    assert _is_private_ip("192.168.1.1") is True
    assert _is_private_ip("172.16.0.1") is True
    assert _is_private_ip("169.254.169.254") is True  # AWS/GCP metadata service
    assert _is_private_ip("8.8.8.8") is False  # Public IP


def test_ssrf_validate_url_safety():
    """Verify URL validation catches internal schemes and unsafe hosts."""
    is_safe, msg = _validate_url_safety("http://127.0.0.1:8000/secret")
    assert is_safe is False
    assert "private/internal" in msg.lower() or "blocked" in msg.lower() or "internal" in msg.lower()

    is_safe, msg = _validate_url_safety("ftp://example.com")
    assert is_safe is False
    assert "Unsupported scheme" in msg

    is_safe, msg = _validate_url_safety("not-a-url")
    assert is_safe is False


# ── 2. Multi-Signal Venture Classifier Tests ────────────────────────────────

def test_classify_fashion_ecommerce():
    """Verify fashion / e-commerce website evidence is classified accurately."""
    classifier = VentureClassifier()
    evidence = {
        "domain": "myntra.com",
        "brand_name": "Myntra",
        "all_headings": ["Men's Clothing", "Women's Footwear", "Flat 50% Off Sale", "Shop Latest Trends"],
        "all_meta_descriptions": ["Online shopping for clothing, shoes, fashion, lifestyle and accessories."],
        "schema_org_types": ["Product", "Offer", "ItemList"],
        "business_model_signals": ["E-commerce / Online Store"],
        "detected_products": ["Running Shoes", "Denim Jacket", "Sneakers"],
        "detected_pricing": ["₹1,999", "₹3,499", "₹799"],
        "pages": [{"body_text_snippet": "Shop online for shoes clothing fashion wear dresses accessories cart checkout"}],
    }

    result = classifier.classify(evidence, user_category_id="fashion-lifestyle")
    assert result.primary_domain == "ecommerce"
    assert result.confidence > 0.6
    assert result.user_category_compatible is True


def test_classify_technology_search():
    """Verify search / internet service (Google-like) is classified as technology."""
    classifier = VentureClassifier()
    evidence = {
        "domain": "google.com",
        "brand_name": "Google",
        "all_headings": ["Search the world's information", "Cloud Solutions", "Developer Tools", "AI Platform"],
        "all_meta_descriptions": ["Search the world's information, including webpages, images, videos and more."],
        "schema_org_types": ["WebApplication", "SoftwareApplication"],
        "business_model_signals": ["Developer Platform / API"],
        "detected_products": ["Google Search", "Google Cloud", "Workspace"],
        "detected_pricing": [],
        "pages": [{"body_text_snippet": "search engine browser cloud software platform api developer ai machine learning tools"}],
    }

    result = classifier.classify(evidence, user_category_id="apps-digital")
    assert result.primary_domain == "technology"
    assert result.confidence > 0.6
    assert result.user_category_compatible is True


def test_classify_restaurant_food_service():
    """Verify food / dining website is classified as food_beverage."""
    classifier = VentureClassifier()
    evidence = {
        "domain": "paradisebiryani.in",
        "brand_name": "Paradise Biryani",
        "all_headings": ["Our Authentic Hyderabadi Menu", "Dine In & Table Reservation", "Order Online Delivery", "Chef's Specials"],
        "all_meta_descriptions": ["Best authentic Hyderabadi Biryani, kebabs, and Mughlai cuisine restaurant."],
        "schema_org_types": ["Restaurant", "FoodEstablishment"],
        "business_model_signals": ["Restaurant / Food Service"],
        "detected_products": ["Mutton Biryani", "Chicken Tikka", "Double Ka Meetha"],
        "detected_pricing": ["₹380", "₹450"],
        "pages": [{"body_text_snippet": "restaurant menu dining cuisine food order delivery chef kitchen meal dinner lunch biryani"}],
    }

    result = classifier.classify(evidence, user_category_id="food-beverage")
    assert result.primary_domain == "food_beverage"
    assert result.confidence > 0.6
    assert result.user_category_compatible is True


def test_classify_saas_software():
    """Verify B2B SaaS platform is classified as technology."""
    classifier = VentureClassifier()
    evidence = {
        "domain": "linear.app",
        "brand_name": "Linear",
        "all_headings": ["Issue Tracking Built for Speed", "API Documentation", "Integrations", "Pricing Plans"],
        "all_meta_descriptions": ["Linear is a purpose-built tool for planning and building software products."],
        "schema_org_types": ["SoftwareApplication"],
        "business_model_signals": ["SaaS / Subscription", "Developer Platform / API"],
        "detected_products": ["Linear Standard", "Linear Enterprise"],
        "detected_pricing": ["$8/user/mo", "$14/user/mo"],
        "pages": [{"body_text_snippet": "software saas issue tracking engineering developer api sync devops cloud platform subscribe"}],
    }

    result = classifier.classify(evidence, user_category_id="apps-digital")
    assert result.primary_domain == "technology"
    assert result.confidence > 0.6


def test_classify_insufficient_evidence():
    """Verify completely empty or sparse evidence reports unknown with insufficient confidence."""
    classifier = VentureClassifier()
    evidence = {
        "domain": "mystery-site.xyz",
        "brand_name": "",
        "all_headings": [],
        "all_meta_descriptions": [],
        "schema_org_types": [],
        "business_model_signals": [],
        "detected_products": [],
        "detected_pricing": [],
        "pages": [{"body_text_snippet": "Hello world welcome"}],
    }

    result = classifier.classify(evidence)
    assert result.primary_domain == "unknown"
    assert result.confidence_label == "insufficient"
    assert result.confidence == 0.0


# ── 3. Category Mismatch Detection Tests ────────────────────────────────────

def test_category_mismatch_detection_google_with_fashion():
    """CRITICAL REQUIREMENT: If user enters google.com with Fashion category, mismatch must be flagged."""
    classifier = VentureClassifier()
    evidence = {
        "domain": "google.com",
        "brand_name": "Google",
        "all_headings": ["Search Engine", "Cloud Software", "Developer API"],
        "all_meta_descriptions": ["Search the world's information."],
        "schema_org_types": ["WebApplication"],
        "business_model_signals": ["Developer Platform / API"],
        "detected_products": [],
        "detected_pricing": [],
        "pages": [{"body_text_snippet": "search engine cloud software api developer internet platform technology"}],
    }

    # User explicitly chose "fashion-lifestyle"
    result = classifier.classify(evidence, user_category_id="fashion-lifestyle")
    assert result.primary_domain == "technology"
    assert result.user_category_compatible is False
    assert "incompatible" in result.mismatch_explanation.lower() or "not compatible" in result.mismatch_explanation.lower()


def test_category_mismatch_detection_saas_with_food():
    """Verify SaaS site with Food category is flagged as a category mismatch."""
    classifier = VentureClassifier()
    evidence = {
        "domain": "stripe.com",
        "brand_name": "Stripe",
        "all_headings": ["Financial Infrastructure for the Internet", "API Reference", "Pricing Plans"],
        "all_meta_descriptions": ["Payment processing platform for internet businesses."],
        "schema_org_types": ["SoftwareApplication"],
        "business_model_signals": ["SaaS / Subscription"],
        "detected_products": [],
        "detected_pricing": ["2.9% + 30¢"],
        "pages": [{"body_text_snippet": "payments software cloud api developers platform fintech banking finance"}],
    }

    # User selected food-beverage
    result = classifier.classify(evidence, user_category_id="food-beverage")
    assert result.user_category_compatible is False


# ── 4. Domain-Specific Recommendation Engine & Intervention Tests ───────────

def test_recommendation_engine_domain_templates():
    """Verify recommendations are tailored to domain."""
    engine = RecommendationEngine()

    ecom_recs = engine.generate_recommendations("ecommerce", "Fashion & Lifestyle")
    assert len(ecom_recs) >= 3
    assert any("discount" in r["title"].lower() or "referral" in r["title"].lower() for r in ecom_recs)

    saas_recs = engine.generate_recommendations("technology", "SaaS")
    assert len(saas_recs) >= 3
    assert any("freemium" in r["title"].lower() or "annual" in r["title"].lower() for r in saas_recs)

    rest_recs = engine.generate_recommendations("food_beverage", "Restaurant")
    assert len(rest_recs) >= 3
    assert any("delivery" in r["title"].lower() or "loyalty" in r["title"].lower() for r in rest_recs)


def test_intervention_computation():
    """Verify intervention calculations apply accurate percentage and absolute deltas."""
    engine = RecommendationEngine()
    rec = {
        "id": "rec_ecom_1",
        "title": "Implement youth discount",
        "simulation_params": {
            "average_order_value_delta_pct": -0.10,
            "monthly_customers_base_delta_pct": 0.20,
        }
    }
    baseline = {"average_order_value": 3000.0, "monthly_customers_base": 500.0}
    intervention = engine.compute_intervention(rec, baseline)

    modified = intervention["modified_assumptions"]
    assert modified["average_order_value"] == 2700.0  # -10%
    assert modified["monthly_customers_base"] == 600.0  # +20%
    assert len(intervention["changes_applied"]) == 2


# ── 5. Dynamic 500-Person Synthetic Population Tests ─────────────────────────

def test_dynamic_population_generator_domains():
    """Verify 500 calibrated participants are generated per domain with appropriate personas."""
    generator = DynamicPopulationGenerator(random_seed=42)

    # Technology domain
    tech_market = generator.generate(
        domain="technology",
        sub_domain="SaaS",
        venture_price=1200.0,
        market_median_price=900.0,
        marketing_budget=150000.0,
    )
    assert tech_market["total_synthetic_cohort"] == 500
    assert len(tech_market["segments"]) >= 4
    # Segments should be tech-specific
    seg_names = [s["name"] for s in tech_market["segments"]]
    assert any("Tech" in n or "Early Adopter" in n or "SMB" in n or "Enterprise" in n for n in seg_names)
    assert tech_market["funnel"]["stages"][0]["count"] == 500
    assert tech_market["funnel"]["final_simulated_customers"] > 0

    # Food & Beverage domain
    food_market = generator.generate(
        domain="food_beverage",
        sub_domain="Restaurant",
        venture_price=600.0,
        market_median_price=500.0,
        marketing_budget=100000.0,
    )
    assert food_market["total_synthetic_cohort"] == 500
    food_seg_names = [s["name"] for s in food_market["segments"]]
    assert any("Foodie" in n or "Family" in n or "Lunch" in n for n in food_seg_names)


# ── 6. VentureAnalysisAgent Pipeline Integration Tests ──────────────────────

@pytest.mark.asyncio
async def test_venture_agent_empty_url_handling():
    """Verify agent handles empty or missing URLs gracefully without throwing errors."""
    agent = VentureAnalysisAgent()
    result = await agent.analyze_venture(venture_url="")

    assert result["has_url"] is False
    assert result["crawled_status"] == "no_url"
    assert result["classification"]["confidence_label"] == "insufficient"
    assert "business_model" in result["xray"]


@pytest.mark.asyncio
async def test_venture_agent_invalid_url_handling():
    """Verify agent handles non-existent or failing domains gracefully with error feedback."""
    agent = VentureAnalysisAgent()
    result = await agent.analyze_venture(
        venture_url="https://non-existent-domain-that-will-fail-dns-resolution-12345.xyz",
        category="Fashion & Lifestyle",
    )

    assert result["has_url"] is True
    assert result["crawled_status"] == "failed"
    assert result["classification"]["primary_domain"] == "unknown"
    assert result["pipeline_status"] == "crawl_failed"
    assert len(result["evidence_summary"]["errors"]) > 0


# ── 7. FastAPI Route Integration Tests ──────────────────────────────────────

@pytest.mark.asyncio
async def test_api_analyze_venture_route():
    """Verify POST /api/ventures/analyze returns structured classification, recommendations, and evidence."""
    from httpx import AsyncClient, ASGITransport
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/ventures/analyze", json={
            "url": "https://example.com",
            "name": "Example Tech",
            "category": "Fashion & Lifestyle",
        })
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "classification" in data["data"]
        assert "xray" in data["data"]
        assert "recommendations" in data["data"]
        assert "hindsight" in data["data"]


@pytest.mark.asyncio
async def test_api_deploy_simulation_domain_agnostic():
    """Verify POST /api/simulation/deploy returns domain-specific population and segments."""
    from httpx import AsyncClient, ASGITransport
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # SaaS / Tech deployment
        res = await client.post("/api/simulation/deploy", json={
            "venture_price": 2500.0,
            "market_median_price": 2000.0,
            "marketing_budget": 120000.0,
            "domain": "technology",
            "sub_domain": "SaaS",
        })
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["total_synthetic_cohort"] == 500
        assert data["domain"] == "technology"
        assert len(data["segments"]) >= 4

        # Food & Beverage deployment
        res_food = await client.post("/api/simulation/deploy", json={
            "venture_price": 450.0,
            "market_median_price": 380.0,
            "marketing_budget": 80000.0,
            "domain": "food_beverage",
            "sub_domain": "Restaurant",
        })
        assert res_food.status_code == 200
        data_food = res_food.json()["data"]
        assert data_food["domain"] == "food_beverage"


@pytest.mark.asyncio
async def test_api_test_intervention_endpoint():
    """Verify POST /api/simulation/test-intervention produces before vs after comparison."""
    from httpx import AsyncClient, ASGITransport
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/simulation/test-intervention", json={
            "recommendation": {
                "id": "rec_test_1",
                "title": "15% Student Discount Program",
                "simulation_params": {
                    "average_order_value_delta_pct": -0.15,
                    "monthly_customers_base_delta_pct": 0.25,
                }
            },
            "current_assumptions": {
                "monthly_customers_base": 500,
                "average_order_value": 3000.0,
                "operating_cost_monthly": 180000.0,
                "marketing_budget_monthly": 150000.0,
                "gross_margin_percent": 0.55,
                "customer_acquisition_cost": 300.0,
                "retention_rate": 0.40,
                "investment_amount": 3000000.0,
            }
        })
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        assert "comparison" in body
        assert "month_12_revenue" in body["comparison"]
        assert "before" in body["comparison"]["month_12_revenue"]
        assert "after" in body["comparison"]["month_12_revenue"]
        assert "impact_summary" in body
        assert len(body["changes_applied"]) == 2

