from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(
    # get_db_url(settings.POSTGRES_DATABASE),
    "postgresql+asyncpg://postgres:postgres@localhost:5432/db_test",
    echo=False,
    future=True,
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

