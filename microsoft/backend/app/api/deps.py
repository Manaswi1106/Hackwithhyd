"""
API Dependencies
Provides dependency injection for database sessions, orchestrator, and Hindsight services.
"""

from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.agents.orchestrator import VentureScopeOrchestrator
from app.hindsight.memory_service import HindsightMemoryService
from app.hindsight.providers import create_hindsight_provider
from app.config import settings

_orchestrator: VentureScopeOrchestrator = None


def get_orchestrator() -> VentureScopeOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = VentureScopeOrchestrator()
    return _orchestrator


def get_hindsight_service() -> HindsightMemoryService:
    provider = create_hindsight_provider(
        api_token=settings.hindsight_api_token,
        base_url=settings.hindsight_api_url,
    )
    return HindsightMemoryService(
        provider=provider,
        bank_id=settings.hindsight_bank_id,
    )
