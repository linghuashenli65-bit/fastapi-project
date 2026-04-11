
import pymysql
from sqlalchemy import text
from backend.core.config import DB_CONFIG
from backend.core.database import AsyncSessionLocal,SyncSessionLocal


def get_connection():
    return pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        cursorclass=pymysql.cursors.DictCursor,
    )


def execute_sql(sql: str) -> list:
    """同步执行原生 SQL，返回字典列表"""
    with SyncSessionLocal() as session:
        result = session.execute(text(sql))
        rows = result.fetchall()
        # 转换为字典列表
        return [dict(row._mapping) for row in rows]