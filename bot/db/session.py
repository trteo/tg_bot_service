from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from settings.config import get_db_url

engine = create_async_engine(
    get_db_url(),
    echo=False,
    future=True,
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

