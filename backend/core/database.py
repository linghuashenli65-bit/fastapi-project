from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from backend.core.config import settings

# ---------- 同步部分 ----------
# 使用 pymysql 驱动（同步）
SYNC_DATABASE_URL = settings.DATABASE_URL.replace("mysql+asyncmy", "mysql+pymysql")

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False,               # 开发时可开启，生产请关闭
    pool_pre_ping=True,      # 连接池健康检查
)

# 同步会话工厂
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

# ---------- 异步部分 ----------
# 使用 asyncmy 驱动（异步）
ASYNC_DATABASE_URL = settings.DATABASE_URL

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 共享的模型基类
Base = declarative_base()

# ---------- 依赖注入函数 ----------
# 异步依赖（用于大多数路由）
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
