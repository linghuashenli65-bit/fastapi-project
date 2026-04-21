"""
教师模块 CRUD 测试
"""
import random
import string

import pytest

from conftest import _rand, _debug_response


@pytest.mark.asyncio
async def test_get_teachers_list(client):
    """测试获取教师列表"""
    resp = await client.get("/teacher/")
    _debug_response(resp, "teachers_list")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1
    assert isinstance(data.get("datas"), list)


@pytest.mark.asyncio
async def test_get_teachers_pagination(client):
    """测试教师列表分页"""
    resp = await client.get("/teacher/?page=1&size=5")
    _debug_response(resp, "teachers_pagination")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_create_teacher(client):
    """测试创建教师"""
    suffix = _rand()
    resp = await client.post("/teacher/", json={
        "name": f"李教授{suffix}",
        "gender": "M",
        "title": "教授",
    })
    _debug_response(resp, "create_teacher")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    if data["status"] == 1:
        assert data["datas"][0].get("teacher_no")


@pytest.mark.asyncio
async def test_get_teacher_by_id(client, existing_teacher):
    """测试按 ID 查询教师"""
    teacher_id = existing_teacher["id"]
    resp = await client.get(f"/teacher/{teacher_id}")
    _debug_response(resp, "teacher_by_id")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_get_teacher_by_no(client, existing_teacher):
    """测试按编号查询教师"""
    teacher_no = existing_teacher["teacher_no"]
    resp = await client.get(f"/teacher/no/{teacher_no}")
    _debug_response(resp, "teacher_by_no")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_get_teacher_not_found(client):
    """测试查询不存在的教师"""
    resp = await client.get("/teacher/999999")
    _debug_response(resp, "teacher_not_found")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 0


@pytest.mark.asyncio
async def test_update_teacher(client, existing_teacher):
    """测试更新教师信息"""
    teacher_id = existing_teacher["id"]
    resp = await client.put(f"/teacher/{teacher_id}", json={
        "name": "更新后教师名",
        "title": "副教授",
    })
    _debug_response(resp, "update_teacher")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_delete_teacher(client):
    """测试删除教师（先创建再删除）"""
    suffix = _rand()
    resp = await client.post("/teacher/", json={
        "name": f"待删除教师{suffix}",
        "gender": "M",
        "title": "讲师",
    })
    _debug_response(resp, "delete_teacher:create")
    body = resp.json()
    if body.get("status") != 1:
        pytest.skip("创建教师失败，跳过删除测试")
    teacher_id = body["datas"][0]["id"]

    resp = await client.delete(f"/teacher/{teacher_id}")
    _debug_response(resp, "delete_teacher:delete")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_get_teachers_by_name(client):
    """测试按姓名模糊查询教师"""
    resp = await client.get("/teacher/?name=测试")
    _debug_response(resp, "teachers_by_name")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1
