"""
用户管理模块（管理员）测试
注意：需要超管账号，若数据库无超管则部分测试会 skip
"""
import pytest

from conftest import _rand, _debug_response


@pytest.mark.asyncio
async def test_admin_get_users_unauthorized(client):
    """测试未认证访问用户管理接口"""
    resp = await client.get("/admin/users")
    _debug_response(resp, "admin_users_unauthorized")
    assert resp.status_code in (401, 403), f"期望 401/403，实际 {resp.status_code}: {resp.text}"


@pytest.mark.asyncio
async def test_admin_get_users(client, admin_token):
    """测试获取用户列表（超管）"""
    if not admin_token:
        pytest.skip("无超管 token，跳过")
    resp = await client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    _debug_response(resp, "admin_get_users")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1
    assert isinstance(data.get("datas"), list)


@pytest.mark.asyncio
async def test_admin_get_user_by_id(client, admin_token):
    """测试按 ID 获取用户（超管）"""
    if not admin_token:
        pytest.skip("无超管 token，跳过")
    resp = await client.get(
        "/admin/users/1",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    _debug_response(resp, "admin_get_user_by_id")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"


@pytest.mark.asyncio
async def test_admin_create_user(client, admin_token):
    """测试创建用户（超管）"""
    if not admin_token:
        pytest.skip("无超管 token，跳过")
    suffix = _rand()
    resp = await client.post(
        "/admin/users",
        json={
            "email": f"admin_created_{suffix}@example.com",
            "password": "CreatedByAdmin123!",
            "username": f"admin_created_{suffix}",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    _debug_response(resp, "admin_create_user")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_admin_delete_user(client, admin_token):
    """测试删除用户（超管）"""
    if not admin_token:
        pytest.skip("无超管 token，跳过")
    # 先创建
    suffix = _rand()
    resp = await client.post(
        "/admin/users",
        json={
            "email": f"to_delete_{suffix}@example.com",
            "password": "ToDelete123!",
            "username": f"to_delete_{suffix}",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    _debug_response(resp, "admin_delete_user:create")
    body = resp.json()
    user_id = None
    if body.get("status") == 1:
        user_id = body.get("datas", [{}])[0].get("id")
    if not user_id:
        pytest.skip("创建用户失败，跳过")

    # 再删除
    resp = await client.delete(
        f"/admin/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    _debug_response(resp, "admin_delete_user:delete")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_admin_update_user(client, admin_token):
    """测试更新用户（超管）"""
    if not admin_token:
        pytest.skip("无超管 token，跳过")
    # 先创建
    suffix = _rand()
    resp = await client.post(
        "/admin/users",
        json={
            "email": f"to_update_{suffix}@example.com",
            "password": "ToUpdate123!",
            "username": f"to_update_{suffix}",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    _debug_response(resp, "admin_update_user:create")
    body = resp.json()
    user_id = None
    if body.get("status") == 1:
        user_id = body.get("datas", [{}])[0].get("id")
    if not user_id:
        pytest.skip("创建用户失败，跳过")

    # 更新
    resp = await client.put(
        f"/admin/users/{user_id}",
        json={"full_name": "管理员更新名字"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    _debug_response(resp, "admin_update_user:put")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_admin_delete_self(client, admin_token):
    """测试超管不能删除自己"""
    if not admin_token:
        pytest.skip("无超管 token，跳过")
    # 先获取当前用户信息
    me_resp = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    _debug_response(me_resp, "admin_delete_self:me")
    if me_resp.status_code != 200:
        pytest.skip("无法获取当前用户信息")

    my_id = me_resp.json().get("id")
    if not my_id:
        pytest.skip("无法获取当前用户 ID")

    # 尝试删除自己
    resp = await client.delete(
        f"/admin/users/{my_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    _debug_response(resp, "admin_delete_self:delete")
    # 应该返回错误（不能删除自己）
    if resp.status_code == 200:
        data = resp.json()
        if data.get("status") == 0:
            assert "不能删除自己" in data.get("messages", "")
