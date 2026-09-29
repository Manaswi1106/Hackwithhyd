"""
Database Connection and Session Management
Supports PostgreSQL (asyncpg) or SQLite fallback for immediate local testing.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings
from app.database.models import Base
import logging

logger = logging.getLogger(__name__)

# Normalize database URL: if postgresql://, use postgresql+asyncpg://
db_url = settings.database_url
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Allow sqlite for standalone execution without a running postgres container
is_sqlite = "sqlite" in db_url

try:
    engine = create_async_engine(
        db_url,
        echo=settings.debug,
        future=True,
    )
except Exception as e:
    logger.warning(f"Could not initialize primary database ({db_url}): {e}. Falling back to sqlite.")
    db_url = "sqlite+aiosqlite:///./venturescope.db"
    engine = create_async_engine(db_url, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db():
    """Create all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
