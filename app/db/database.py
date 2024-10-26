from app.db.models import Base
from app.core.config import settings
from app.utils.logging import setup_logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# set sqlalchemy logger
setup_logger("sqlalchemy")

# async engine and session
engine = create_async_engine(settings.database_url, echo=True)
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    await engine.dispose()
