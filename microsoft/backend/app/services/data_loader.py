"""
Data Loader Service for VentureScope
Dynamically loads empirical datasets from CSV files:
- areas.csv
- historical_sales.csv
- competitor_reference.csv

NO values exist inside Python code. Everything loads dynamically from disk.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class MarketDataLoader:
    _areas_cache: Optional[List[Dict[str, Any]]] = None
    _sales_cache: Optional[List[Dict[str, Any]]] = None
    _competitors_cache: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def load_areas(cls, force_reload: bool = False) -> List[Dict[str, Any]]:
        """Load 15+ commercial localities from areas.csv."""
        if cls._areas_cache is not None and not force_reload:
            return cls._areas_cache

        filepath = DATA_DIR / "areas.csv"
        if not filepath.exists():
            raise FileNotFoundError(f"areas.csv not found at {filepath}")

        areas = []
        with open(filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                areas.append({
                    "area": row["area"],
                    "city": row["city"],
                    "population": int(row["population"]),
                    "avg_income": float(row["avg_income"]),
                    "daily_footfall": int(row["daily_footfall"]),
                    "avg_rent_sqft": float(row["avg_rent_sqft"]),
                    "office_density": float(row["office_density"]),
                    "road_connectivity": float(row["road_connectivity"]),
                    "parking_score": float(row["parking_score"]),
                    "metro_distance": float(row["metro_distance"]),
                    "competitor_count": int(row["competitor_count"]),
                    "restaurant_count": int(row["restaurant_count"]),
                    "lat": float(row["lat"]),
                    "lng": float(row["lng"]),
                })
        cls._areas_cache = areas
        return areas

    @classmethod
    def load_historical_sales(cls, force_reload: bool = False) -> List[Dict[str, Any]]:
        """Load historical retail/commercial sales from historical_sales.csv."""
        if cls._sales_cache is not None and not force_reload:
            return cls._sales_cache

        filepath = DATA_DIR / "historical_sales.csv"
        if not filepath.exists():
            raise FileNotFoundError(f"historical_sales.csv not found at {filepath}")

        sales = []
        with open(filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sales.append({
                    "area": row["area"],
                    "category": row["category"],
                    "store_size_sqft": float(row["store_size_sqft"]),
                    "monthly_sales": float(row["monthly_sales"]),
                    "avg_ticket_size": float(row["avg_ticket_size"]),
                    "operating_months": int(row["operating_months"]),
                    "seasonality_index": float(row["seasonality_index"]),
                })
        cls._sales_cache = sales
        return sales

    @classmethod
    def load_competitor_reference(cls, force_reload: bool = False) -> List[Dict[str, Any]]:
        """Load reference competitors from competitor_reference.csv."""
        if cls._competitors_cache is not None and not force_reload:
            return cls._competitors_cache

        filepath = DATA_DIR / "competitor_reference.csv"
        if not filepath.exists():
            raise FileNotFoundError(f"competitor_reference.csv not found at {filepath}")

        competitors = []
        with open(filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                competitors.append({
                    "area": row["area"],
                    "business_name": row["business_name"],
                    "category": row["category"],
                    "rating": float(row["rating"]),
                    "review_count": int(row["review_count"]),
                    "lat": float(row["lat"]),
                    "lng": float(row["lng"]),
                    "price_level": row["price_level"],
                })
        cls._competitors_cache = competitors
        return competitors
