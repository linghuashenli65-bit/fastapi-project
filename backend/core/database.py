from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings import settings

# 拼接数据库地址
# MySQL：mysql+pymysql://用户:密码@主机:端口/库名
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# 创建引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# 会话类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 模型基类
Base = declarative_base()

# 数据库依赖（给API用）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()