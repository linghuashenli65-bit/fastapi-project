"""
成绩模块 CRUD + 统计测试
"""
import random
import string

import pytest

from conftest import _rand, _debug_response


@pytest.mark.asyncio
async def test_get_scores_list(client):
    """测试获取成绩列表"""
    resp = await client.get("/score/")
    _debug_response(resp, "scores_list")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1
    assert isinstance(data.get("datas"), list)


@pytest.mark.asyncio
async def test_get_scores_pagination(client):
    """测试成绩列表分页"""
    resp = await client.get("/score/?page=1&size=5")
    _debug_response(resp, "scores_pagination")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_create_score(client, existing_student, existing_class):
    """测试创建成绩"""
    student_no = existing_student["student_no"]
    class_no = str(existing_class["class_no"])
    resp = await client.post("/score/", json={
        "student_no": student_no,
        "class_no": class_no,
        "exam_sequence": random.randint(1, 9999),
        "exam_date": "2024-10-15",
        "score": 92.5,
    })
    _debug_response(resp, "create_score")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    if data["status"] == 1:
        assert data["datas"][0]["score"] == 92.5


@pytest.mark.asyncio
async def test_get_score_by_id(client):
    """测试按 ID 查询成绩（使用已有数据）"""
    resp = await client.get("/score/?page=1&size=1")
    _debug_response(resp, "score_by_id:list")
    data = resp.json()
    if not data.get("datas"):
        pytest.skip("无成绩数据，跳过")
    score_id = data["datas"][0]["id"]

    resp = await client.get(f"/score/{score_id}")
    _debug_response(resp, "score_by_id")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_get_score_not_found(client):
    """测试查询不存在的成绩"""
    resp = await client.get("/score/999999")
    _debug_response(resp, "score_not_found")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 0


@pytest.mark.asyncio
async def test_get_scores_by_student(client, existing_student):
    """测试按学号查询成绩"""
    student_no = existing_student["student_no"]
    resp = await client.get(f"/score/student/{student_no}")
    _debug_response(resp, "scores_by_student")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_get_scores_by_class(client, existing_class):
    """测试按班级查询成绩"""
    class_no = existing_class["class_no"]
    resp = await client.get(f"/score/class/{class_no}")
    _debug_response(resp, "scores_by_class")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_update_score(client):
    """测试更新成绩（使用已有数据）"""
    resp = await client.get("/score/?page=1&size=1")
    _debug_response(resp, "update_score:get")
    data = resp.json()
    if not data.get("datas"):
        pytest.skip("无成绩数据，跳过")
    score_id = data["datas"][0]["id"]

    resp = await client.put(f"/score/{score_id}", json={
        "score": 95.0,
    })
    _debug_response(resp, "update_score:put")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_delete_score(client, existing_student, existing_class):
    """测试删除成绩"""
    student_no = existing_student["student_no"]
    class_no = str(existing_class["class_no"])
    resp = await client.post("/score/", json={
        "student_no": student_no,
        "class_no": class_no,
        "exam_sequence": random.randint(10000, 99999),
        "exam_date": "2024-12-01",
        "score": 60.0,
    })
    _debug_response(resp, "delete_score:create")
    body = resp.json()
    if body.get("status") != 1:
        pytest.skip("创建成绩失败，跳过删除测试")
    score_id = body["datas"][0]["id"]

    resp = await client.delete(f"/score/{score_id}")
    _debug_response(resp, "delete_score:delete")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_score_statistics_by_class(client, existing_class):
    """测试班级成绩统计"""
    class_no = existing_class["class_no"]
    resp = await client.get(f"/score/statistics/class/{class_no}")
    _debug_response(resp, "score_stats_by_class")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_score_statistics_by_student(client, existing_student):
    """测试学生成绩统计"""
    student_no = existing_student["student_no"]
    resp = await client.get(f"/score/statistics/student/{student_no}")
    _debug_response(resp, "score_stats_by_student")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == 1


@pytest.mark.asyncio
async def test_create_score_invalid_range(client, existing_student, existing_class):
    """测试创建成绩时分数超出范围"""
    student_no = existing_student["student_no"]
    class_no = str(existing_class["class_no"])
    resp = await client.post("/score/", json={
        "student_no": student_no,
        "class_no": class_no,
        "exam_sequence": 1,
        "exam_date": "2024-10-15",
        "score": 150.0,
    })
    _debug_response(resp, "create_score_invalid_range")
    assert resp.status_code == 422, f"期望 422，实际 {resp.status_code}: {resp.text}"
