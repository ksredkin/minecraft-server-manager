from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.common.core.config import secrets, settings

url = f"postgresql+asyncpg://{settings.db_user}:{secrets.get('db_password')}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

async_engine: AsyncEngine = create_async_engine(
    url,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True,
    pool_timeout=5,
)
session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine, expire_on_commit=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, Any]:
    async with session() as db_session:
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise
