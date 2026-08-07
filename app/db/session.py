# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Ek engine banana hoga — ye connection pool hai jo Postgres se actual network connections manage karta hai.
# Ek session factory banani hogi — session ek "conversation" hai DB ke sath ek request ke duration ke liye (query karo, insert karo, phir close kar do).
# Ek helper function (get_db) banayenge jo FastAPI ko har incoming request pe ek fresh session dega, aur request khatam hote hi auto-close kar dega.