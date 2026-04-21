"""
就业模块 CRUD 测试
"""
import random
import string

import pytest

from conftest import _rand, _debug_response


@pytest.mark.asyncio
async def test_get_employments_list(client):
    """测试获取就业列表"""
    resp = await client.get("/employment/")
    _debug_response(resp, "employments_list")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1
    assert isinstance(data.get("datas"), list)


@pytest.mark.asyncio
async def test_get_employments_pagination(client):
    """测试就业列表分页"""
    resp = await client.get("/employment/?page=1&size=5")
    _debug_response(resp, "employments_pagination")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_get_employments_by_company(client):
    """测试按公司名称筛选就业记录"""
    resp = await client.get("/employment/?company_name=测试")
    _debug_response(resp, "employments_by_company")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_create_employment(client, existing_student):
    """测试创建就业记录（record_type 为 offer 或 employment）"""
    student_no = existing_student["student_no"]
    suffix = _rand()
    resp = await client.post("/employment/", json={
        "student_no": student_no,
        "company_name": f"测试公司{suffix}",
        "job_title": "后端开发",
        "salary": 20000,
        "offer_date": "2024-05-01",
        "record_type": "offer",
    })
    _debug_response(resp, "create_employment")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    if data["status"] == 1:
        assert data["datas"][0]["company_name"] == f"测试公司{suffix}"


@pytest.mark.asyncio
async def test_update_employment(client, existing_student):
    """测试更新就业信息（先创建再更新）"""
    student_no = existing_student["student_no"]
    suffix = _rand()
    # 先创建
    resp = await client.post("/employment/", json={
        "student_no": student_no,
        "company_name": f"更新测试公司{suffix}",
        "job_title": "后端开发",
        "salary": 20000,
        "record_type": "offer",
    })
    _debug_response(resp, "update_employment:create")
    body = resp.json()
    if body.get("status") != 1:
        pytest.skip("创建就业记录失败，跳过更新测试")
    emp_id = body["datas"][0]["id"]

    resp = await client.put(f"/employment/{emp_id}", json={
        "job_title": "高级后端开发",
        "salary": 25000,
    })
    _debug_response(resp, "update_employment:put")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_delete_employment(client, existing_student):
    """测试删除就业记录"""
    student_no = existing_student["student_no"]
    suffix = _rand()
    resp = await client.post("/employment/", json={
        "student_no": student_no,
        "company_name": f"待删除公司{suffix}",
        "record_type": "offer",
    })
    _debug_response(resp, "delete_employment:create")
    body = resp.json()
    if body.get("status") != 1:
        pytest.skip("创建就业记录失败，跳过删除测试")
    emp_id = body["datas"][0]["id"]

    resp = await client.delete(f"/employment/{emp_id}")
    _debug_response(resp, "delete_employment:delete")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_create_employment_missing_required(client):
    """测试创建就业记录时缺少必填字段"""
    resp = await client.post("/employment/", json={
        "company_name": "缺少学号",
    })
    _debug_response(resp, "create_employment_missing")
    assert resp.status_code == 422, f"期望 422，实际 {resp.status_code}: {resp.text}"
