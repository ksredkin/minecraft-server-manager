from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

url = f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}"

async_engine: AsyncEngine = create_async_engine(url, pool_size=10, max_overflow=20, pool_recycle=3600, pool_pre_ping=True, pool_timeout=5)
session: async_sessionmaker = async_sessionmaker(bind=async_engine, expire_on_commit=False)

@asynccontextmanager
async def get_db_session() -> AsyncGenerator[Any, Any, AsyncSession]:
    async with session() as db_session:
        db_session: AsyncSession
        try:
            yield db_session
            db_session.commit()
            db_session.close()
        except Exception:
            db_session.rollback()
            raise
