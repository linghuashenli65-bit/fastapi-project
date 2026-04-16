from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_async_db
from backend.services.class_service import class_service
from backend.schemas.Class import ClassUpdate, ClassCreate

router = APIRouter()

@router.get("/", response_model=dict, summary="分页获得班级列表，按班级姓名模糊查找（可选）")
async def get_classes(db: AsyncSession = Depends(get_async_db), skip: int = 0, limit: int = 100):
    """获取班级分页列表"""
    return await class_service.get_paginated_classes(db, skip=skip, limit=limit)


@router.post("/", response_model=ClassCreate, summary="创建新班级")
async def create_class(
    new_class: ClassCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """创建新班级"""
    try:
        new_class = await class_service.create_class(db, new_class)
        return new_class
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{class_id}", response_model=ClassUpdate, summary="修改班级信息")
async def update_class(
        class_id: int,
        class_in: ClassUpdate,
        db: AsyncSession = Depends(get_async_db),
):
    """更新班级信息"""
    try:
        return await class_service.update_class(db, class_id, class_in)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))


@router.delete("/{class_id}", summary="删除班级")
async def delete_class(class_id: int, db: AsyncSession = Depends(get_async_db)):
    """删除班级"""
    return await class_service.delete_class(db, class_id)


@router.get("/{class_no}", response_model=list, summary="查看班级内部学生信息与教师信息")
async def get_class_members(class_no: str, db: AsyncSession = Depends(get_async_db)):
    """获取班级成员信息"""
    try:
        return await class_service.get_class_members(db, class_no)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))
