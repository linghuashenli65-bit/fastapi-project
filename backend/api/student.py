from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_async_db
from backend.services.student_service import student_service
from backend.schemas.student import StudentCreate, StudentUpdate, StudentInDB, StudentOut

router = APIRouter()

@router.get("/", response_model=dict, summary="分页获得学生列表，按学生姓名模糊查找（可选）")
async def get_students(page: int = 1, size: int = 10, name: str = None, db: AsyncSession = Depends(get_async_db)):
    """获取学生分页列表"""
    result = await student_service.get_paginated_students(db, page=page, size=size, name=name)
    return result


@router.get("/{student_id}", response_model=StudentOut, summary="按学生ID查询学生")
async def get_student_by_id(student_id: int, db: AsyncSession = Depends(get_async_db)):
    """按学生ID查询"""
    student = await student_service.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.get("/no/{student_no}", response_model=StudentInDB, summary="按学号查询学生")
async def get_student_by_no(student_no: str, db: AsyncSession = Depends(get_async_db)):
    """按学号查询"""
    student = await student_service.get_student_by_no(db, student_no)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post("/", response_model=StudentCreate, summary="创建学生")
async def create_student(student_in: StudentCreate, db: AsyncSession = Depends(get_async_db)):
    """创建新学生"""
    return await student_service.create_student(db, student_in)


@router.put("/{student_id}", response_model=StudentUpdate, summary="修改学生信息")
async def update_student(student_id: int, student_in: StudentUpdate, db: AsyncSession = Depends(get_async_db)):
    """更新学生信息"""
    try:
        student = await student_service.update_student(db, student_id, student_in)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))
    return student


@router.delete("/{student_id}", summary="删除学生")
async def delete_student(student_id: int, db: AsyncSession = Depends(get_async_db)):
    """删除学生"""
    student = await student_service.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    await student_service.delete_student(db, str(student_id))
    return {"message": "删除成功"}
