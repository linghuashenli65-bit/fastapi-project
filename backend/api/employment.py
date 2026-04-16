from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_async_db
from backend.services.employment_service import employment_service
from backend.schemas.employment import EmploymentCreate, EmploymentUpdate, EmploymentOutDB

router = APIRouter()

@router.get("/", response_model=dict, summary="分页获得就业列表,可以按公司名称筛选")
async def get_employment(page: int = 1, size: int = 10, company_name: str = None, db: AsyncSession = Depends(get_async_db)):
    """获取就业信息分页列表"""
    result = await employment_service.get_paginated_employment(db, page=page, size=size, company_name=company_name)
    return result


@router.post("/", response_model=EmploymentCreate, summary="创建就业信息")
async def create_employment(employment_in: EmploymentCreate, db: AsyncSession = Depends(get_async_db)):
    """创建就业信息"""
    return await employment_service.create_employment(db, employment_in)


@router.put("/{id}", response_model=EmploymentUpdate, summary="修改就业信息")
async def update_employment(id: int, employment_in: EmploymentUpdate, db: AsyncSession = Depends(get_async_db)):
    """更新就业信息"""
    try:
        return await employment_service.update_employment(db, id, employment_in)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))


@router.delete("/{id}", summary="删除就业信息")
async def delete_employment(id: int, db: AsyncSession = Depends(get_async_db)):
    """删除就业信息"""
    try:
        return await employment_service.delete_employment(db, id)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))
