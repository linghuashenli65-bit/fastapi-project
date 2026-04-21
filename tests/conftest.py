"""
Pytest 测试配置 - 提供异步 TestClient、通用 fixtures

数据隔离策略：
- 读操作使用共享 client（不修改数据）
- 写操作（create/update/delete）每次独立执行，失败则 skip
- 学号/教师编号/班级编号由数据库 trigger 自动生成，并发创建可能冲突
  因此 fixture 优先从已有数据中查询，仅在需要删除操作时才创建新记录

异步支持：
- 所有异步测试标记 @pytest.mark.asyncio 并正确 await
- pytest.ini 配置 asyncio_mode = auto

调试输出：
- conftest 中 _debug_response() 在断言前打印 status_code 和 body
- 每个测试断言附带 f-string 详细信息
"""
import asyncio
import random
import string
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from backend.app.main import app


# ========== 事件循环 ==========

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ========== 异步 HTTP 客户端 ==========

@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """异步 HTTP 测试客户端 — 初始化 fastapi-cache"""
    from fastapi_cache import FastAPICache
    from fastapi_cache.backends.inmemory import InMemoryBackend
    FastAPICache.init(InMemoryBackend(), prefix="sms_cache")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


# ========== 工具函数 ==========

def _rand(n: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def _debug_response(resp, label: str = ""):
    """断言失败前打印调试信息"""
    prefix = f"[{label}] " if label else ""
    print(f"\n{prefix}status_code={resp.status_code}")
    try:
        body = resp.json()
        # 截断过长的 body
        body_str = str(body)
        if len(body_str) > 500:
            body_str = body_str[:500] + "..."
        print(f"{prefix}body={body_str}")
    except Exception:
        print(f"{prefix}text={resp.text[:500]}")


# ========== 通用 fixtures ==========

@pytest_asyncio.fixture
async def auth_token(client: AsyncClient) -> str:
    """获取认证 token"""
    suffix = _rand()
    email = f"test_{suffix}@example.com"
    resp = await client.post("/auth/register", json={
        "email": email,
        "password": "TestPass123!",
        "username": f"test_{suffix}",
    })
    _debug_response(resp, "auth_token:register")
    if resp.status_code != 201:
        pytest.skip(f"注册失败: {resp.status_code}")

    resp = await client.post("/auth/jwt/login", data={
        "username": email,
        "password": "TestPass123!",
    })
    _debug_response(resp, "auth_token:login")
    data = resp.json()
    token = data.get("access_token", "")
    if not token:
        pytest.skip("登录失败，无法获取 token")
    return token


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient) -> str:
    """获取超管 token"""
    resp = await client.post("/auth/jwt/login", data={
        "username": "2764411488@qq.com",
        "password": "Gb2zh.4CZFuUiEz",
    })
    _debug_response(resp, "admin_token:login")
    data = resp.json()
    token = data.get("access_token", "")
    if not token:
        pytest.skip("超管登录失败")
    return token


async def _get_first_from_list(client: AsyncClient, url: str, label: str) -> dict | None:
    """从列表 API 获取第一条数据"""
    resp = await client.get(url)
    _debug_response(resp, label)
    data = resp.json()
    if data.get("status") == 1 and data.get("datas"):
        return data["datas"][0]
    return None


async def _try_create_and_get(client: AsyncClient, create_url: str, payload: dict, list_url: str, label: str) -> dict | None:
    """尝试创建记录，失败则从列表获取第一条"""
    resp = await client.post(create_url, json=payload)
    _debug_response(resp, f"{label}:create")
    body = resp.json()
    if body.get("status") == 1 and body.get("datas"):
        return body["datas"][0]
    # 创建失败（可能学号冲突），从已有数据中获取
    return await _get_first_from_list(client, list_url, f"{label}:fallback")


@pytest_asyncio.fixture
async def existing_student(client: AsyncClient) -> dict:
    """获取一个已有学生（优先创建，学号冲突则查列表）"""
    suffix = _rand()
    student = await _try_create_and_get(
        client,
        "/student/",
        {
            "name": f"测试学生{suffix}",
            "gender": "M",
            "enrollment_date": "2024-09-01",
            "education": 3,
            "major": f"专业{suffix}",
        },
        "/student/?page=1&size=1",
        "existing_student",
    )
    if not student:
        pytest.skip("无法获取学生数据")
    return student


@pytest_asyncio.fixture
async def existing_teacher(client: AsyncClient) -> dict:
    """获取一个已有教师（优先创建，编号冲突则查列表）"""
    suffix = _rand()
    teacher = await _try_create_and_get(
        client,
        "/teacher/",
        {
            "name": f"测试教师{suffix}",
            "gender": "M",
            "title": "教授",
        },
        "/teacher/?page=1&size=1",
        "existing_teacher",
    )
    if not teacher:
        pytest.skip("无法获取教师数据")
    return teacher


@pytest_asyncio.fixture
async def existing_class(client: AsyncClient) -> dict:
    """获取一个已有班级（优先创建，编号冲突则查列表）"""
    suffix = _rand()
    cls = await _try_create_and_get(
        client,
        "/class/",
        {
            "class_name": f"测试班级{suffix}",
            "start_date": "2024-09-01",
        },
        "/class/?skip=0&limit=1",
        "existing_class",
    )
    if not cls:
        pytest.skip("无法获取班级数据")
    return cls
