"""
FastAPI-Users 单元测试
使用 pytest 和 FastAPI TestClient
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.core.database import Base, get_async_db
from backend.models.user import User


# 创建异步测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """初始化测试数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def override_get_db():
    """覆盖数据库依赖"""
    async with TestingSessionLocal() as session:
        yield session


# 覆盖依赖
app.dependency_overrides[get_async_db] = override_get_db


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    """设置测试数据库"""
    await init_db()
    yield
    # 清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client():
    """创建异步测试客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def test_user_data():
    """测试用户数据"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123",
        "username": "testuser",
        "full_name": "测试用户",
        "phone": "13800138000"
    }


class TestUserRegistration:
    """用户注册测试"""
    
    @pytest.mark.asyncio
    async def test_register_success(self, async_client, test_user_data):
        """测试成功注册"""
        response = await async_client.post("/auth/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, async_client, test_user_data):
        """测试重复邮箱注册"""
        # 第一次注册
        await async_client.post("/auth/register", json=test_user_data)
        
        # 第二次注册（应该失败）
        response = await async_client.post("/auth/register", json=test_user_data)
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client):
        """测试无效邮箱格式"""
        response = await async_client.post("/auth/register", json={
            "email": "invalid-email",
            "password": "TestPassword123"
        })
        assert response.status_code == 422


class TestUserLogin:
    """用户登录测试"""
    
    @pytest.fixture(autouse=True)
    async def setup_user(self, async_client, test_user_data):
        """设置：先注册一个用户"""
        await async_client.post("/auth/register", json=test_user_data)
    
    @pytest.mark.asyncio
    async def test_login_success(self, async_client, test_user_data):
        """测试成功登录"""
        response = await async_client.post(
            "/auth/jwt/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, async_client, test_user_data):
        """测试错误密码"""
        response = await async_client.post(
            "/auth/jwt/login",
            data={
                "username": test_user_data["email"],
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 400


class TestUserProfile:
    """用户信息测试"""
    
    @pytest_asyncio.fixture
    async def auth_token(self, async_client, test_user_data):
        """获取认证 token"""
        # 注册用户
        await async_client.post("/auth/register", json=test_user_data)
        
        # 登录获取 token
        response = await async_client.post(
            "/auth/jwt/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        return response.json()["access_token"]
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, async_client, auth_token, test_user_data):
        """测试获取当前用户信息"""
        response = await async_client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_auth(self, async_client):
        """测试未认证访问"""
        response = await async_client.get("/users/me")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_openapi_docs(async_client):
    """测试 OpenAPI 文档是否生成"""
    response = await async_client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_openapi_json(async_client):
    """测试 OpenAPI JSON 是否生成"""
    response = await async_client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "paths" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
