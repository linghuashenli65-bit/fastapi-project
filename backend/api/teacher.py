from fastapi import HTTPException, APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_async_db
from backend.services.teacher_service import teacher_service
from backend.schemas.teacher import TeacherInDB, TeacherOut, TeacherCreate, TeacherUpdate

router = APIRouter()

@router.get("/", response_model=dict, summary="分页获得教师列表，按教师姓名模糊查找（可选）")
async def get_teachers(page: int = 1, size: int = 10, name: str = None, db: AsyncSession = Depends(get_async_db)):
    """获取教师分页列表"""
    result = await teacher_service.get_paginated_teachers(db, page=page, size=size, name=name)
    return result


@router.get("/no/{teacher_no}", summary="按教师编号查询教师")
async def get_teacher_by_no(teacher_no: int, db: AsyncSession = Depends(get_async_db)):
    """按教师编号查询"""
    teacher = await teacher_service.get_teacher_by_no(db, teacher_no)
    if not teacher:
        raise HTTPException(status_code=404, detail="未找到该教师")
    return teacher


@router.get("/{teacher_id}", summary="按教师ID查询教师")
async def get_teacher_by_id(teacher_id: int, db: AsyncSession = Depends(get_async_db)):
    """按教师ID查询"""
    teacher = await teacher_service.get_teacher_by_id(db, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="未找到该教师")
    return teacher


@router.post("/", response_model=TeacherInDB, summary="添加新教师")
async def create_teacher(teacher_in: TeacherCreate, db: AsyncSession = Depends(get_async_db)):
    """创建新教师"""
    try:
        teacher = await teacher_service.create_teacher(db, teacher_in)
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))
    return teacher


@router.put("/{teacher_id}", response_model=TeacherInDB, summary="修改教师信息")
async def update_teacher(teacher_id: int, teacher_in: TeacherUpdate, db: AsyncSession = Depends(get_async_db)):
    """更新教师信息"""
    try:
        teacher = await teacher_service.update_teacher(db, teacher_id, teacher_in)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))
    return teacher


@router.delete("/{teacher_id}", summary="删除教师")
async def delete_teacher(teacher_id: int, db: AsyncSession = Depends(get_async_db)):
    """删除教师"""
    teacher = await teacher_service.get_teacher_by_id(db, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="未找到该教师")
    
    await teacher_service.delete_teacher(db, teacher_id)
    return {"message": "删除成功"}
