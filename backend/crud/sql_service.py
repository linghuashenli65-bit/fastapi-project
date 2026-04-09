
import pymysql

from backend.core.config import DB_CONFIG
from backend.core.database import engine

def get_connection():
    return pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        cursorclass=pymysql.cursors.DictCursor,
    )

def execute_sql(sql: str):
    #数据库连接
    connection = engine.raw_connection()
    try:
        cursor = connection.cursor()
        # 关键：临时禁用 ONLY_FULL_GROUP_BY 和相关的严格模式
        cursor.execute("SET SESSION sql_mode = ''")
        cursor.execute(sql)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in result]
    finally:
        cursor.close()
        connection.close()