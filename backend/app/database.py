"""
Motor de base de datos con lazy initialization.
Los engines se crean solo cuando se necesitan por primera vez,
lo que permite que los tests sobreescriban las dependencias
sin requerir psycopg2 / asyncpg instalados.
"""
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Lazy: se inicializan en la primera llamada
_sync_engine = None
_async_engine = None
_async_session_local = None


def _get_sync_engine():
    global _sync_engine
    if _sync_engine is None:
        _sync_engine = create_engine(
            settings.DATABASE_URL_SYNC,
            echo=settings.DEBUG,
            pool_pre_ping=True,
        )
    return _sync_engine


def _get_async_engine():
    global _async_engine
    if _async_engine is None:
        _async_engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
        )
    return _async_engine


def _get_async_session_local():
    global _async_session_local
    if _async_session_local is None:
        _async_session_local = sessionmaker(
            bind=_get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _async_session_local


# Exponer sync_engine como variable de módulo (retrocompatibilidad con conftest)
# Se evalúa cuando se accede, no al importar
class _LazyEngine:
    """Proxy para que `from app.database import sync_engine` funcione."""
    def __getattr__(self, item):
        return getattr(_get_sync_engine(), item)


sync_engine = _LazyEngine()  # type: ignore[assignment]


async def get_db() -> AsyncSession:
    async with _get_async_session_local()() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_db_and_tables():
    async with _get_async_engine().begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


def get_sync_db():
    with Session(_get_sync_engine()) as session:
        try:
            yield session
        finally:
            session.close()
