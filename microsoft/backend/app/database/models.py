"""
SQLAlchemy Database Models for VentureScope Platform

Tables:
- users
- ventures
- markets
- market_categories
- companies
- competitors
- products
- locations
- location_metrics
- customer_segments
- market_metrics
- sources
- evidence
- venture_observations
- simulation_runs
- simulation_assumptions
- simulation_results
- market_events
- analysis_runs
"""

from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    ForeignKey, Text, JSON, Enum as SQLEnum, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    ventures = relationship("Venture", back_populates="user", cascade="all, delete-orphan")


class MarketCategory(Base):
    __tablename__ = "market_categories"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    icon = Column(String(32), nullable=True)
    parent_id = Column(String(64), ForeignKey("market_categories.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    subcategories = relationship("MarketCategory", backref="parent", remote_side=[id])
    markets = relationship("Market", back_populates="category")


class Market(Base):
    __tablename__ = "markets"

    id = Column(String(64), primary_key=True, index=True)
    city_id = Column(String(64), nullable=False, index=True)
    city_name = Column(String(128), nullable=False)
    category_id = Column(String(64), ForeignKey("market_categories.id"), nullable=False)
    subcategory_id = Column(String(64), nullable=False)
    category_name = Column(String(128), nullable=False)
    subcategory_name = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    category = relationship("MarketCategory", back_populates="markets")
    ventures = relationship("Venture", back_populates="market")
    competitors = relationship("Competitor", back_populates="market")
    customer_segments = relationship("CustomerSegment", back_populates="market")
    analysis_runs = relationship("AnalysisRun", back_populates="market")


class Venture(Base):
    __tablename__ = "ventures"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=True, index=True)
    market_id = Column(String(64), ForeignKey("markets.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)
    deployment_model = Column(String(64), default="hybrid")  # online, physical, hybrid, multi-location
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="ventures")
    market = relationship("Market", back_populates="ventures")
    observations = relationship("VentureObservation", back_populates="venture", cascade="all, delete-orphan")
    simulation_runs = relationship("SimulationRun", back_populates="venture", cascade="all, delete-orphan")
    analysis_runs = relationship("AnalysisRun", back_populates="venture")


class Company(Base):
    __tablename__ = "companies"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    website = Column(String(512), nullable=True)
    headquarters = Column(String(255), nullable=True)
    founded_year = Column(Integer, nullable=True)
    overview = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(String(64), primary_key=True, index=True)
    market_id = Column(String(64), ForeignKey("markets.id"), nullable=False, index=True)
    company_id = Column(String(64), ForeignKey("companies.id"), nullable=True)
    name = Column(String(255), nullable=False)
    category = Column(String(128), nullable=False)
    positioning = Column(String(64), nullable=False)  # budget, mid-range, premium, luxury
    price_min = Column(Float, nullable=False, default=0.0)
    price_max = Column(Float, nullable=False, default=0.0)
    target_audience = Column(JSON, default=list)
    customer_segments = Column(JSON, default=list)
    major_locations = Column(JSON, default=list)
    popular_products = Column(JSON, default=list)
    evidence_type = Column(String(32), default="observed")  # observed, inferred, modeled
    source_url = Column(String(512), nullable=True)
    confidence = Column(String(32), default="high")
    position_x = Column(Float, default=50.0)  # for 2D positioning map
    position_y = Column(Float, default=50.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    market = relationship("Market", back_populates="competitors")
    products = relationship("Product", back_populates="competitor", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id = Column(String(64), primary_key=True, index=True)
    competitor_id = Column(String(64), ForeignKey("competitors.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(128), nullable=True)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    features = Column(JSON, default=list)
    evidence_type = Column(String(32), default="observed")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    competitor = relationship("Competitor", back_populates="products")


class Location(Base):
    __tablename__ = "locations"

    id = Column(String(64), primary_key=True, index=True)
    city_id = Column(String(64), nullable=False, index=True)
    city_name = Column(String(128), nullable=False)
    name = Column(String(128), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    characteristics = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class LocationMetric(Base):
    __tablename__ = "location_metrics"

    id = Column(String(64), primary_key=True, index=True)
    location_id = Column(String(64), ForeignKey("locations.id"), nullable=False, index=True)
    market_id = Column(String(64), ForeignKey("markets.id"), nullable=False, index=True)
    analysis_run_id = Column(String(64), nullable=True, index=True)
    competitor_density = Column(Integer, default=0)
    customer_concentration = Column(Float, default=0.0)
    demand_signal = Column(String(32), default="medium")  # high, medium, low
    average_price = Column(Float, default=0.0)
    opportunity_signal = Column(String(32), default="medium")  # high, medium, low
    opportunity_score = Column(Float, default=50.0)
    target_audience = Column(JSON, default=list)
    observed_activity = Column(String(128), nullable=True)
    evidence_type = Column(String(32), default="modeled")
    confidence = Column(String(32), default="medium")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class CustomerSegment(Base):
    __tablename__ = "customer_segments"

    id = Column(String(64), primary_key=True, index=True)
    market_id = Column(String(64), ForeignKey("markets.id"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    icon = Column(String(32), nullable=True)
    demand_signal = Column(String(32), default="medium")
    typical_spend = Column(Float, default=0.0)
    typical_spend_range = Column(JSON, default=dict)
    price_sensitivity = Column(String(32), default="medium")
    purchase_frequency = Column(String(64), default="Monthly")
    preferences = Column(JSON, default=list)
    motivations = Column(JSON, default=list)
    objections = Column(JSON, default=list)
    discovery_channels = Column(JSON, default=list)
    purchase_triggers = Column(JSON, default=list)
    repeat_purchase_signal = Column(String(32), default="medium")
    fit_score = Column(Float, default=70.0)
    evidence_type = Column(String(32), default="modeled")
    confidence = Column(String(32), default="medium")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    market = relationship("Market", back_populates="customer_segments")


class Source(Base):
    __tablename__ = "sources"

    id = Column(String(64), primary_key=True, index=True)
    url = Column(String(1024), nullable=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(64), default="web")  # web, news, directory, maps, social
    retrieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    raw_content = Column(Text, nullable=True)
    meta = Column(JSON, default=dict)


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(64), primary_key=True, index=True)
    source_id = Column(String(64), ForeignKey("sources.id"), nullable=True)
    market_id = Column(String(64), nullable=True, index=True)
    venture_id = Column(String(64), nullable=True, index=True)
    claim = Column(Text, nullable=False)
    quote = Column(Text, nullable=True)
    evidence_type = Column(String(32), default="observed")  # observed, inferred, modeled, simulated
    confidence = Column(String(32), default="medium")
    metric_field = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class VentureObservation(Base):
    __tablename__ = "venture_observations"

    id = Column(String(64), primary_key=True, index=True)
    venture_id = Column(String(64), ForeignKey("ventures.id"), nullable=False, index=True)
    analysis_run_id = Column(String(64), nullable=True, index=True)
    business_model = Column(String(255), nullable=True)
    product = Column(String(255), nullable=True)
    price_point = Column(String(255), nullable=True)
    target_audience = Column(Text, nullable=True)
    positioning = Column(String(255), nullable=True)
    differentiators = Column(JSON, default=list)
    competitive_overlap = Column(JSON, default=list)
    strength_signals = Column(JSON, default=list)
    risk_signals = Column(JSON, default=list)
    evidence_type = Column(String(32), default="inferred")
    confidence = Column(String(32), default="medium")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    venture = relationship("Venture", back_populates="observations")


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(String(64), primary_key=True, index=True)
    venture_id = Column(String(64), ForeignKey("ventures.id"), nullable=True, index=True)
    market_id = Column(String(64), ForeignKey("markets.id"), nullable=False, index=True)
    deployment_model = Column(String(64), default="hybrid")
    target_location = Column(String(128), nullable=True)
    break_even_month_expected = Column(Integer, nullable=True)
    recovery_month_expected = Column(Integer, nullable=True)
    total_investment = Column(Float, default=0.0)
    month_12_revenue_expected = Column(Float, default=0.0)
    month_12_profit_expected = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    venture = relationship("Venture", back_populates="simulation_runs")
    assumptions = relationship("SimulationAssumption", back_populates="simulation_run", uselist=False, cascade="all, delete-orphan")
    results = relationship("SimulationResult", back_populates="simulation_run", cascade="all, delete-orphan")


class SimulationAssumption(Base):
    __tablename__ = "simulation_assumptions"

    id = Column(String(64), primary_key=True, index=True)
    simulation_run_id = Column(String(64), ForeignKey("simulation_runs.id"), nullable=False, unique=True)
    monthly_customers_base = Column(Integer, default=500)
    customer_acquisition_cost = Column(Float, default=300.0)
    average_order_value = Column(Float, default=1500.0)
    purchase_frequency = Column(Float, default=1.5)
    retention_rate = Column(Float, default=0.4)
    operating_cost_monthly = Column(Float, default=250000.0)
    marketing_budget_monthly = Column(Float, default=150000.0)
    gross_margin_percent = Column(Float, default=0.55)
    investment_amount = Column(Float, default=3000000.0)
    growth_rate_monthly = Column(Float, default=0.08)
    churn_rate = Column(Float, default=0.05)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    simulation_run = relationship("SimulationRun", back_populates="assumptions")


class SimulationResult(Base):
    __tablename__ = "simulation_results"

    id = Column(String(64), primary_key=True, index=True)
    simulation_run_id = Column(String(64), ForeignKey("simulation_runs.id"), nullable=False, index=True)
    scenario = Column(String(32), nullable=False)  # optimistic, expected, pessimistic
    break_even_month = Column(Integer, nullable=True)
    recovery_month = Column(Integer, nullable=True)
    total_investment_required = Column(Float, default=0.0)
    monthly_breakdown = Column(JSON, default=list)  # list of 24 months metrics
    final_metrics = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    simulation_run = relationship("SimulationRun", back_populates="results")


class MarketEvent(Base):
    __tablename__ = "market_events"

    id = Column(String(64), primary_key=True, index=True)
    market_id = Column(String(64), ForeignKey("markets.id"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)  # competitor_entry, price_shift, demand_spike, location_shift
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    metric_changes = Column(JSON, default=dict)
    occurred_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    hindsight_memory_id = Column(String(128), nullable=True)


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(String(64), primary_key=True, index=True)
    market_id = Column(String(64), ForeignKey("markets.id"), nullable=False, index=True)
    venture_id = Column(String(64), ForeignKey("ventures.id"), nullable=True, index=True)
    status = Column(String(32), default="pending")  # pending, researching, analyzing, simulating, complete, error
    progress = Column(Integer, default=0)
    stages = Column(JSON, default=list)
    hindsight_state_stored = Column(Boolean, default=False)
    hindsight_changes_detected = Column(JSON, default=list)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    market = relationship("Market", back_populates="analysis_runs")
    venture = relationship("Venture", back_populates="analysis_runs")
