from core.config import settings
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

dsn = (
    f'postgresql+asyncpg://{settings.postgres.user}:{settings.postgres.password}@'
    f'{settings.postgres.host}:{settings.postgres.port}/{settings.postgres.dbname}'
)

engine = create_async_engine(dsn, echo=settings.debug, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
