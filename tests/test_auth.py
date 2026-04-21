"""
认证模块测试
"""
import random
import string

import pytest

from conftest import _rand, _debug_response


@pytest.mark.asyncio
async def test_register(client):
    """测试用户注册"""
    suffix = _rand()
    email = f"reg_{suffix}@example.com"
    resp = await client.post("/auth/register", json={
        "email": email,
        "password": "RegPass123!",
        "username": f"reg_{suffix}",
    })
    _debug_response(resp, "register")
    # fastapi-users 注册成功返回 201
    assert resp.status_code == 201, f"期望 201，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["email"] == email
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    """测试重复邮箱注册"""
    suffix = _rand()
    email = f"dup_{suffix}@example.com"
    payload = {
        "email": email,
        "password": "DupPass123!",
        "username": f"dup_{suffix}",
    }
    resp1 = await client.post("/auth/register", json=payload)
    _debug_response(resp1, "dup_register_1")
    assert resp1.status_code == 201

    resp2 = await client.post("/auth/register", json=payload)
    _debug_response(resp2, "dup_register_2")
    assert resp2.status_code in (400, 409), f"期望 400/409，实际 {resp2.status_code}: {resp2.text}"


@pytest.mark.asyncio
async def test_login_success(client):
    """测试登录成功"""
    suffix = _rand()
    email = f"login_{suffix}@example.com"
    resp = await client.post("/auth/register", json={
        "email": email,
        "password": "LoginPass123!",
        "username": f"login_{suffix}",
    })
    _debug_response(resp, "login_register")

    resp = await client.post("/auth/jwt/login", data={
        "username": email,
        "password": "LoginPass123!",
    })
    _debug_response(resp, "login")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """测试错误密码登录"""
    suffix = _rand()
    email = f"wrongpw_{suffix}@example.com"
    await client.post("/auth/register", json={
        "email": email,
        "password": "RightPass123!",
        "username": f"wrongpw_{suffix}",
    })
    resp = await client.post("/auth/jwt/login", data={
        "username": email,
        "password": "WrongPass123!",
    })
    _debug_response(resp, "login_wrong_pw")
    assert resp.status_code == 400, f"期望 400，实际 {resp.status_code}: {resp.text}"


@pytest.mark.asyncio
async def test_get_current_user(client, auth_token):
    """测试获取当前用户信息"""
    if not auth_token:
        pytest.skip("未获取到 token")
    resp = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    _debug_response(resp, "get_current_user")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "email" in data


@pytest.mark.asyncio
async def test_update_current_user(client, auth_token):
    """测试更新当前用户信息"""
    if not auth_token:
        pytest.skip("未获取到 token")
    resp = await client.patch(
        "/users/me",
        json={"full_name": "测试全名"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    _debug_response(resp, "update_current_user")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("full_name") == "测试全名"


@pytest.mark.asyncio
async def test_logout(client, auth_token):
    """测试登出"""
    if not auth_token:
        pytest.skip("未获取到 token")
    resp = await client.post(
        "/auth/jwt/logout",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    _debug_response(resp, "logout")
    assert resp.status_code in (200, 204), f"期望 200/204，实际 {resp.status_code}: {resp.text}"


@pytest.mark.asyncio
async def test_unauthorized_access(client):
    """测试未认证访问受保护资源"""
    resp = await client.get("/users/me")
    _debug_response(resp, "unauthorized")
    assert resp.status_code in (401, 403), f"期望 401/403，实际 {resp.status_code}: {resp.text}"
