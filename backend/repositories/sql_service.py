import aiomysql
import pymysql
from backend.core.config import DB_CONFIG
from sqlalchemy import text
from backend.core.database import async_engine
from decimal import Decimal

def get_connection():
    return pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        cursorclass=pymysql.cursors.DictCursor,
    )

def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    return obj

async def execute_sql(sql: str):
    async with async_engine.connect() as conn:
        await conn.execute(text("SET SESSION sql_mode = ''"))
        result = await conn.execute(text(sql))
        if result.returns_rows:
            # 关键：将 RowMapping 转换为字典
            rows = [dict(row) for row in result.mappings()]
            return convert_decimal(rows)
        else:
            return {"affected_rows": result.rowcount}
