from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.repositories.student_repo import student_repo
from backend.schemas.student import StudentCreate, StudentUpdate, StudentOut, StudentInDB
from backend.models.student import Student


class StudentService:
    """学生业务逻辑层"""
    
    def __init__(self):
        self.repo = student_repo
    
    async def get_paginated_students(
        self, 
        db: AsyncSession, 
        page: int = 1, 
        size: int = 10, 
        name: Optional[str] = None
    ) -> dict:
        """分页获取学生列表"""
        filters = {}
        if name:
            filters["name"] = f"%{name}%"
        
        result = await self.repo.paginate(
            db,
            page=page,
            page_size=size,
            filters=filters,
            order_by="created_at",
            descending=True
        )
        # 转换为输出模型
        result["data"] = [StudentOut.model_validate(item) for item in result["data"]]
        return result
    
    async def get_student_by_id(self, db: AsyncSession, student_id: int) -> Optional[StudentOut]:
        """按学生ID查询"""
        student = await self.repo.get(db, student_id)
        if not student:
            return None
        return StudentOut.model_validate(student)
    
    async def get_student_by_no(self, db: AsyncSession, student_no: str) -> Optional[StudentInDB]:
        """按学号查询"""
        return await self.repo.get_by_student_no(db, student_no)
    
    async def create_student(self, db: AsyncSession, student_in: StudentCreate) -> Student:
        """创建学生"""
        # 可以添加业务逻辑，如生成学号等
        return await self.repo.create(db, obj_in=student_in)
    
    async def update_student(
        self, 
        db: AsyncSession, 
        student_id: int, 
        student_in: StudentUpdate
    ) -> Student:
        """更新学生信息"""
        student = await self.repo.get(db, student_id)
        if not student:
            raise ValueError("Student not found")
        
        return await self.repo.update(db, db_obj=student, obj_in=student_in)
    
    async def delete_student(self, db: AsyncSession, student_no: str) -> bool:
        """删除学生"""
        student = await self.repo.get_by_student_no(db, student_no)
        if not student:
            raise ValueError("Student not found")
        
        return await self.repo.remove(db, db_obj=student, id=student.id)


# 创建单例实例
student_service = StudentService()
