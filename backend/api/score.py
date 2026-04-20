from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from backend.core.database import get_async_db
from backend.services.score_service import score_service
from backend.schemas.score import ScoreCreate, ScoreUpdate
from backend.core.response import UnifiedResponse
from backend.core.config import settings
from backend.utils.helpers import cache_key_builder

router = APIRouter()


@router.get("/", summary="分页获取成绩列表")
@cache(expire=settings.CACHE_LIST_EXPIRE, key_builder=cache_key_builder)
async def get_scores(
    page: int = Query(1, description="页码"),
    size: int = Query(10, description="每页数量"),
    db: AsyncSession = Depends(get_async_db)
):
    """获取成绩分页列表"""
    result = await score_service.get_scores(db, page=page, page_size=size)
    return UnifiedResponse.success(
        datas=result.get("data", []),
        messages="查询成功",
        count=result.get("count", 0),
        page=page,
        page_size=size,
    )


@router.get("/{score_id}", summary="按ID查询成绩")
async def get_score_by_id(
    score_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """按成绩ID查询"""
    score = await score_service.get_score_by_id(db, score_id)
    if not score:
        return UnifiedResponse.error(messages="成绩记录不存在")
    return UnifiedResponse.success(datas=[score], messages="查询成功")


@router.get("/student/{student_no}", summary="按学号查询成绩")
@cache(expire=settings.CACHE_LIST_EXPIRE, key_builder=cache_key_builder)
async def get_scores_by_student(
    student_no: str,
    page: int = Query(1, description="页码"),
    size: int = Query(10, description="每页数量"),
    db: AsyncSession = Depends(get_async_db)
):
    """按学号查询学生的成绩列表"""
    result = await score_service.get_scores_by_student(db, student_no=student_no, page=page, page_size=size)
    return UnifiedResponse.success(
        datas=result.get("data", []),
        messages="查询成功",
        count=result.get("count", 0),
        page=page,
        page_size=size,
    )


@router.get("/class/{class_no}", summary="按班级查询成绩")
@cache(expire=settings.CACHE_LIST_EXPIRE, key_builder=cache_key_builder)
async def get_scores_by_class(
    class_no: str,
    page: int = Query(1, description="页码"),
    size: int = Query(10, description="每页数量"),
    db: AsyncSession = Depends(get_async_db)
):
    """按班级查询成绩列表"""
    result = await score_service.get_scores_by_class(db, class_no=class_no, page=page, page_size=size)
    return UnifiedResponse.success(
        datas=result.get("data", []),
        messages="查询成功",
        count=result.get("count", 0),
        page=page,
        page_size=size,
    )


@router.post("/", summary="创建成绩")
async def create_score(
    score_in: ScoreCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """创建新成绩记录"""
    try:
        score = await score_service.create_score(db, score_in)
        return UnifiedResponse.success(datas=[score], messages="创建成功")
    except ValueError as err:
        return UnifiedResponse.error(messages=str(err))


@router.put("/{score_id}", summary="修改成绩")
async def update_score(
    score_id: int,
    score_in: ScoreUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """更新成绩信息"""
    try:
        score = await score_service.update_score(db, score_id, score_in)
        return UnifiedResponse.success(datas=[score], messages="更新成功")
    except ValueError as err:
        return UnifiedResponse.error(messages=str(err))


@router.delete("/{score_id}", summary="删除成绩")
async def delete_score(
    score_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """删除成绩记录"""
    try:
        await score_service.delete_score(db, score_id)
        return UnifiedResponse.success(messages="删除成功")
    except ValueError as err:
        return UnifiedResponse.error(messages=str(err))


@router.get("/statistics/class/{class_no}", summary="班级成绩统计")
@cache(expire=settings.CACHE_LIST_EXPIRE, key_builder=cache_key_builder)
async def get_class_statistics(
    class_no: str,
    db: AsyncSession = Depends(get_async_db)
):
    """获取班级成绩统计"""
    result = await score_service.get_class_statistics(db, class_no=class_no)
    return UnifiedResponse.success(datas=[result], messages="查询成功")


@router.get("/statistics/student/{student_no}", summary="学生成绩统计")
@cache(expire=settings.CACHE_LIST_EXPIRE, key_builder=cache_key_builder)
async def get_student_statistics(
    student_no: str,
    db: AsyncSession = Depends(get_async_db)
):
    """获取学生成绩统计"""
    result = await score_service.get_student_statistics(db, student_no=student_no)
    return UnifiedResponse.success(datas=[result], messages="查询成功")
