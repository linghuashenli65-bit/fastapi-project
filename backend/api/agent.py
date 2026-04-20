import json

import uvicorn
from fastapi import APIRouter, HTTPException

from backend.repositories.sql_service import execute_sql
from backend.models.agent import dispatch_agent, generate_sql, agent_sql
from backend.models.dashboard import build_dashboard
from backend.schemas.agent import SQLRequest, QueryRequest, DashboardRequest
from backend.core.response import UnifiedResponse
from backend.core.config import settings
from fastapi.responses import StreamingResponse

router = APIRouter()

# -------------------------------
# 1. Agent SQL 普通查询接口
# -------------------------------
@router.post("/sql", summary="ai查询接口")
async def agent_sql_api(req: QueryRequest):
    try:
        data = await agent_sql(req.query, req.model)
        return UnifiedResponse.success(datas=[data], messages="查询成功")
    except Exception as e:
        return UnifiedResponse.error(messages=str(e))

# -------------------------------
# 2. Agent调度
# -------------------------------
@router.post("/dispatch", summary="ai调度接口（测试）")
def dispatch_api(req: QueryRequest):
    data = dispatch_agent(req.query)
    return UnifiedResponse.success(datas=[data], messages="调度成功")


# -------------------------------
# 3. SQL生成
# -------------------------------
@router.post("/generate", summary="sql生成接口（测试）")
def generate_sql_api(req: QueryRequest):
    sql = generate_sql(req.query)
    return UnifiedResponse.success(datas=[{"sql": sql}], messages="生成成功")


# -------------------------------
# 4. SQL执行
# -------------------------------
@router.post("/execute", summary="sql执行接口（测试）")
def execute_sql_api(req: SQLRequest):
    try:
        data = execute_sql(req.sql)
        return UnifiedResponse.success(datas=[data], messages="执行成功")
    except Exception as e:
        return UnifiedResponse.error(messages=str(e))



# -------------------------------
# 5. ai分析接口
# -------------------------------
@router.post("/dashboard", summary="AI分析流式接口")
async def dashboard_stream(req: DashboardRequest):
    async def event_generator():
        async for event in build_dashboard(req.query, req.model, req.analysis_length):
            # 将字典转换为 SSE 格式的字符串
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == '__main__':
    uvicorn.run(router, host="0.0.0.0", port=8888)
