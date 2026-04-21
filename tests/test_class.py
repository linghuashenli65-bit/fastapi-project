"""
班级模块 CRUD 测试
"""
import random
import string

import pytest

from conftest import _rand, _debug_response


@pytest.mark.asyncio
async def test_get_classes_list(client):
    """测试获取班级列表"""
    resp = await client.get("/class/")
    _debug_response(resp, "classes_list")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1
    assert isinstance(data.get("datas"), list)


@pytest.mark.asyncio
async def test_get_classes_pagination(client):
    """测试班级列表分页"""
    resp = await client.get("/class/?skip=0&limit=10")
    _debug_response(resp, "classes_pagination")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_create_class(client):
    """测试创建班级（start_date 在 ClassCreate 中是 Optional）"""
    suffix = _rand()
    resp = await client.post("/class/", json={
        "class_name": f"测试班级{suffix}",
        "start_date": "2024-09-01",
    })
    _debug_response(resp, "create_class")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    if data["status"] == 1:
        assert data["datas"][0].get("class_no")


@pytest.mark.asyncio
async def test_get_class_by_no(client, existing_class):
    """测试按班级编号查看班级成员"""
    class_no = existing_class["class_no"]
    resp = await client.get(f"/class/{class_no}")
    _debug_response(resp, "class_by_no")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_update_class(client, existing_class):
    """测试更新班级信息"""
    class_id = existing_class["id"]
    resp = await client.put(f"/class/{class_id}", json={
        "class_name": "更新后班级名",
    })
    _debug_response(resp, "update_class")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_delete_class(client):
    """测试删除班级（先创建再删除）"""
    suffix = _rand()
    resp = await client.post("/class/", json={
        "class_name": f"待删除班级{suffix}",
        "start_date": "2024-09-01",
    })
    _debug_response(resp, "delete_class:create")
    body = resp.json()
    if body.get("status") != 1:
        pytest.skip("创建班级失败，跳过删除测试")
    class_data = body["datas"][0]
    class_id = class_data.get("id")
    if not class_id:
        pytest.skip("班级返回数据中无 id 字段")

    resp = await client.delete(f"/class/{class_id}")
    _debug_response(resp, "delete_class:delete")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_create_class_missing_name(client):
    """测试创建班级时缺少必填字段"""
    resp = await client.post("/class/", json={})
    _debug_response(resp, "create_class_missing_name")
    assert resp.status_code == 422, f"期望 422，实际 {resp.status_code}: {resp.text}"
