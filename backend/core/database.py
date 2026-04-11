from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# ---------- 同步部分 ----------
# 使用 pymysql 驱动（同步）
SYNC_DATABASE_URL = "mysql+pymysql://root:8312460@localhost:3306/student_management_system"

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=True,               # 开发时可开启，生产请关闭
    pool_pre_ping=True,      # 连接池健康检查
)

# 同步会话工厂
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

# ---------- 异步部分 ----------
# 使用 aiomysql 驱动（异步）
ASYNC_DATABASE_URL = "mysql+aiomysql://root:8312460@localhost:3306/student_management_system"

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
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

# 同步依赖（用于需要使用同步会话的路由）
# 注意：FastAPI 的依赖可以是同步函数，但该函数会在异步事件循环中运行，
# 内部的同步数据库操作会阻塞事件循环。推荐两种用法：
# 1. 只在同步路由中使用（def 而不是 async def）
# 2. 在异步路由中用 asyncio.to_thread() 包裹
def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()