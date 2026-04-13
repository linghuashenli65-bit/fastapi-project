from typing import Optional

from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    model: str="qwen"


class SQLRequest(BaseModel):
    sql: str

class DashboardRequest(BaseModel):
    query: str
    model: str="qwen"
    analysis_length: Optional[str] = "medium"