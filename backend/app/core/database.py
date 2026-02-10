from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

Base = declarative_base()

_engine = None
AsyncSessionLocal = None  # keep this name for compatibility


def _init_engine_and_sessionmaker():
    global _engine, AsyncSessionLocal
    if _engine is None:
        _engine = create_async_engine(settings.DATABASE_URL, echo=False)
        AsyncSessionLocal = sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    return _engine


async def get_db():
    # Lazily initialize so demo endpoints can run without DB plumbing.
    if AsyncSessionLocal is None:
        _init_engine_and_sessionmaker()
    async with AsyncSessionLocal() as session:
        yield session