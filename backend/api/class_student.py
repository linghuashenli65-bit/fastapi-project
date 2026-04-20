from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from backend.core.database import get_async_db
from backend.services.class_service import class_service
from backend.schemas.Class import ClassUpdate, ClassCreate
from backend.core.response import UnifiedResponse
from backend.core.config import settings
from backend.utils.helpers import cache_key_builder

router = APIRouter()


@router.get("/", summary="分页获得班级列表，按班级姓名模糊查找（可选）")
@cache(expire=settings.CACHE_LIST_EXPIRE, key_builder=cache_key_builder)
async def get_classes(db: AsyncSession = Depends(get_async_db), skip: int = 0, limit: int = 100):
    """获取班级分页列表"""
    result = await class_service.get_paginated_classes(db, skip=skip, limit=limit)
    return UnifiedResponse.success(
        datas=result["data"],
        messages="查询成功",
        count=result["count"],
    )


@router.post("/", summary="创建新班级")
async def create_class(
    new_class: ClassCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """创建新班级"""
    try:
        new_class = await class_service.create_class(db, new_class)
        return UnifiedResponse.success(datas=[new_class], messages="创建成功")
    except Exception as e:
        return UnifiedResponse.error(messages=str(e))


@router.put("/{class_id}", summary="修改班级信息")
async def update_class(
        class_id: int,
        class_in: ClassUpdate,
        db: AsyncSession = Depends(get_async_db),
):
    """更新班级信息"""
    try:
        result = await class_service.update_class(db, class_id, class_in)
        return UnifiedResponse.success(datas=[result], messages="更新成功")
    except ValueError as err:
        return UnifiedResponse.error(messages=str(err))


@router.delete("/{class_id}", summary="删除班级")
async def delete_class(class_id: int, db: AsyncSession = Depends(get_async_db)):
    """删除班级"""
    result = await class_service.delete_class(db, class_id)
    if result:
        return UnifiedResponse.success(messages="删除成功")
    return UnifiedResponse.error(messages="班级不存在")


@router.get("/{class_no}", summary="查看班级内部学生信息与教师信息")
async def get_class_members(class_no: str, db: AsyncSession = Depends(get_async_db)):
    """获取班级成员信息"""
    try:
        members = await class_service.get_class_members(db, class_no)
        return UnifiedResponse.success(datas=members, messages="查询成功")
    except ValueError as err:
        return UnifiedResponse.error(messages=str(err))
