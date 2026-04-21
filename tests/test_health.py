"""
健康检查与根路径测试
"""
import pytest


@pytest.mark.asyncio
async def test_health(client):
    """测试健康检查接口"""
    resp = await client.get("/health")
    print(f"\n[health] status={resp.status_code}, body={resp.json()}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_root(client):
    """测试根路径返回登录页面"""
    resp = await client.get("/")
    print(f"\n[root] status={resp.status_code}")
    assert resp.status_code == 200
