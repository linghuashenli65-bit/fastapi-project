import json

import uvicorn
from fastapi import APIRouter, HTTPException

from backend.repositories.sql_service import execute_sql
from backend.models.agent import dispatch_agent, generate_sql, agent_sql
from backend.models.dashboard import build_dashboard
from backend.schemas.agent import SQLRequest, QueryRequest, DashboardRequest
from fastapi.responses import StreamingResponse

router = APIRouter()
# 允许跨域
# -------------------------------
# 1. Agent SQL 普通查询接口
# -------------------------------
@router.post("/sql", summary="ai查询接口")
async def agent_sql_api(req: QueryRequest):
    try:
        data = await agent_sql(req.query, req.model)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------
# 2. Agent调度
# -------------------------------
@router.post("/dispatch", summary="ai调度接口（测试）")
def dispatch_api(req: QueryRequest):
    return dispatch_agent(req.query)


# -------------------------------
# 3. SQL生成
# -------------------------------
@router.post("/generate", summary="sql生成接口（测试）")
def generate_sql_api(req: QueryRequest):
    sql = generate_sql(req.query)
    return {"code": 200, "sql": sql}


# -------------------------------
# 4. SQL执行
# -------------------------------
@router.post("/execute", summary="sql执行接口（测试）")
def execute_sql_api(req: SQLRequest):
    try:
        data = execute_sql(req.sql)
        return {"code": 200, "data": data}
    except Exception as e:
        return {"code": 500, "msg": str(e)}



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
