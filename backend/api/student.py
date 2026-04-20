from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from backend.core.database import get_async_db
from backend.services.student_service import student_service
from backend.schemas.student import StudentCreate, StudentUpdate, StudentInDB, StudentOut
from backend.core.response import UnifiedResponse
from backend.core.config import settings
from backend.utils.helpers import cache_key_builder

router = APIRouter()


@router.get("/", summary="分页获得学生列表，按学生姓名模糊查找（可选）")
@cache(expire=settings.CACHE_LIST_EXPIRE, key_builder=cache_key_builder)
async def get_students(page: int = 1, size: int = 10, name: str = None, db: AsyncSession = Depends(get_async_db)):
    """获取学生分页列表"""
    result = await student_service.get_paginated_students(db, page=page, size=size, name=name)
    return UnifiedResponse.success(
        datas=result["data"],
        messages="查询成功",
        count=result["count"],
        page=page,
        page_size=size,
    )


@router.get("/{student_id}", summary="按学生ID查询学生")
async def get_student_by_id(student_id: int, db: AsyncSession = Depends(get_async_db)):
    """按学生ID查询"""
    student = await student_service.get_student_by_id(db, student_id)
    if not student:
        return UnifiedResponse.error(messages="学生不存在")
    return UnifiedResponse.success(datas=[student], messages="查询成功")


@router.get("/no/{student_no}", summary="按学号查询学生")
async def get_student_by_no(student_no: str, db: AsyncSession = Depends(get_async_db)):
    """按学号查询"""
    student = await student_service.get_student_by_no(db, student_no)
    if not student:
        return UnifiedResponse.error(messages="学生不存在")
    return UnifiedResponse.success(datas=[student], messages="查询成功")


@router.post("/", summary="创建学生")
async def create_student(student_in: StudentCreate, db: AsyncSession = Depends(get_async_db)):
    """创建新学生"""
    student = await student_service.create_student(db, student_in)
    return UnifiedResponse.success(datas=[student], messages="创建成功")


@router.put("/{student_id}", summary="修改学生信息")
async def update_student(student_id: int, student_in: StudentUpdate, db: AsyncSession = Depends(get_async_db)):
    """更新学生信息"""
    try:
        student = await student_service.update_student(db, student_id, student_in)
    except ValueError as err:
        return UnifiedResponse.error(messages=str(err))
    return UnifiedResponse.success(datas=[student], messages="更新成功")


@router.delete("/{student_id}", summary="删除学生")
async def delete_student(student_id: int, db: AsyncSession = Depends(get_async_db)):
    """删除学生"""
    student = await student_service.get_student_by_id(db, student_id)
    if not student:
        return UnifiedResponse.error(messages="学生不存在")
    
    await student_service.delete_student(db, str(student_id))
    return UnifiedResponse.success(messages="删除成功")
