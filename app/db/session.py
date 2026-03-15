from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create the async engine using the database URL from settings
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

# Create a sessionmaker factory that will generate AsyncSession instances
AsyncSessionLocal = sessionmaker(
    autoflush=False,
    class_=AsyncSession,
    autocommit=False,
    bind=engine,
)

# Dependency function to get a database session
async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()