from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from config import settings

DATABASE_URL = rf"mysql+aiomysql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}/{settings.DATABASE}"
SYNC_DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}/{settings.DATABASE}"

Base = declarative_base()

async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=1500,
    pool_size=8,
    max_overflow=5,
    pool_timeout=15,
)

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=5,
    max_overflow=2,
)

SyncSessionLocal = sessionmaker(bind=sync_engine)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
)
