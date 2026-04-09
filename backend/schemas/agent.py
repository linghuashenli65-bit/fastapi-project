from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str


class SQLRequest(BaseModel):
    sql: str
