from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from backend.core.database import get_async_db
from backend.services.employment_service import employment_service
from backend.schemas.employment import EmploymentCreate, EmploymentUpdate, EmploymentOutDB
from backend.core.response import UnifiedResponse
from backend.core.config import settings
from backend.utils.helpers import cache_key_builder

router = APIRouter()


@router.get("/", summary="分页获得就业列表,可以按公司名称筛选")
@cache(expire=settings.CACHE_LIST_EXPIRE, key_builder=cache_key_builder)
async def get_employment(page: int = 1, size: int = 10, company_name: str = None, db: AsyncSession = Depends(get_async_db)):
    """获取就业信息分页列表"""
    result = await employment_service.get_paginated_employment(db, page=page, size=size, company_name=company_name)
    return UnifiedResponse.success(
        datas=result["data"],
        messages="查询成功",
        count=result["count"],
        page=page,
        page_size=size,
    )


@router.post("/", summary="创建就业信息")
async def create_employment(employment_in: EmploymentCreate, db: AsyncSession = Depends(get_async_db)):
    """创建就业信息"""
    employment = await employment_service.create_employment(db, employment_in)
    return UnifiedResponse.success(datas=[employment], messages="创建成功")


@router.put("/{id}", summary="修改就业信息")
async def update_employment(id: int, employment_in: EmploymentUpdate, db: AsyncSession = Depends(get_async_db)):
    """更新就业信息"""
    try:
        employment = await employment_service.update_employment(db, id, employment_in)
        return UnifiedResponse.success(datas=[employment], messages="更新成功")
    except ValueError as err:
        return UnifiedResponse.error(messages=str(err))


@router.delete("/{id}", summary="删除就业信息")
async def delete_employment(id: int, db: AsyncSession = Depends(get_async_db)):
    """删除就业信息"""
    try:
        await employment_service.delete_employment(db, id)
        return UnifiedResponse.success(messages="删除成功")
    except ValueError as err:
        return UnifiedResponse.error(messages=str(err))
