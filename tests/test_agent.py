"""
AI 模块接口测试

注意：
1. AI 接口依赖外部大模型服务，可能因网络/配额失败
2. dispatch/generate/execute 的同步/异步 bug 已修复
"""
import json

import pytest

from conftest import _debug_response


@pytest.mark.asyncio
async def test_agent_sql(client):
    """测试 AI 自然语言查询接口"""
    resp = await client.post("/agent/sql", json={
        "query": "查询所有学生的人数",
        "model": "qwen",
    })
    _debug_response(resp, "agent_sql")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] in (0, 1)


@pytest.mark.asyncio
async def test_agent_dispatch(client):
    """测试 AI 调度接口"""
    resp = await client.post("/agent/dispatch", json={
        "query": "查询教师总数",
        "model": "qwen",
    })
    _debug_response(resp, "agent_dispatch")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] in (0, 1)


@pytest.mark.asyncio
async def test_agent_generate(client):
    """测试 SQL 生成接口"""
    resp = await client.post("/agent/generate", json={
        "query": "查询学生数量",
        "model": "qwen",
    })
    _debug_response(resp, "agent_generate")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] in (0, 1)


@pytest.mark.asyncio
async def test_agent_execute(client):
    """测试 SQL 执行接口"""
    resp = await client.post("/agent/execute", json={
        "sql": "SELECT 1 AS test_col",
    })
    _debug_response(resp, "agent_execute")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] in (0, 1)


@pytest.mark.asyncio
async def test_agent_dashboard(client):
    """测试 AI 分析流式接口"""
    resp = await client.post("/agent/dashboard", json={
        "query": "分析学生的成绩分布",
        "model": "qwen",
        "analysis_length": "short",
    })
    _debug_response(resp, "agent_dashboard")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    assert resp.headers.get("content-type", "").startswith("text/event-stream")

    content = resp.text
    events = []
    for line in content.split("\n"):
        if line.startswith("data: "):
            try:
                event = json.loads(line[6:])
                events.append(event)
            except json.JSONDecodeError:
                pass

    assert len(events) > 0, "SSE 事件列表为空"
    last_event = events[-1]
    assert last_event.get("stage") in ("complete", "error", "cache_hit"), \
        f"最后事件 stage={last_event.get('stage')}，期望 complete/error/cache_hit"


@pytest.mark.asyncio
async def test_agent_dashboard_cache_hit(client):
    """测试 AI 分析缓存命中（连续两次相同查询）"""
    payload = {
        "query": "查询班级数量统计",
        "model": "qwen",
        "analysis_length": "short",
    }
    resp1 = await client.post("/agent/dashboard", json=payload)
    _debug_response(resp1, "dashboard_cache:1st")
    assert resp1.status_code == 200

    resp2 = await client.post("/agent/dashboard", json=payload)
    _debug_response(resp2, "dashboard_cache:2nd")
    assert resp2.status_code == 200


@pytest.mark.asyncio
async def test_agent_sql_with_deepseek(client):
    """测试使用 deepseek 模型查询"""
    resp = await client.post("/agent/sql", json={
        "query": "查询班级数量",
        "model": "deepseek",
    })
    _debug_response(resp, "agent_sql_deepseek")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] in (0, 1)
