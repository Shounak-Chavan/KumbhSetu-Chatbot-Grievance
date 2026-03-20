import asyncio

from app.db.session import engine
from app.db.base import Base

from app.models.complaint import Complaint
from app.models.user import User
from app.models.token import RefreshToken

async def init_db():
    # Create all tables in the database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())