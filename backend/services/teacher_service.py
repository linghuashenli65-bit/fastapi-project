from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.repositories.teacher_repo import teacher_repo
from backend.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherOut, TeacherInDB
from backend.models.teacher import Teacher


class TeacherService:
    """教师业务逻辑层"""
    
    def __init__(self):
        self.repo = teacher_repo
    
    async def get_paginated_teachers(
        self, 
        db: AsyncSession, 
        page: int = 1, 
        size: int = 10, 
        name: Optional[str] = None
    ) -> dict:
        """分页获取教师列表"""
        filters = {}
        if name:
            filters["name"] = f"%{name}%"
        
        result = await self.repo.paginate(
            db,
            page=page,
            page_size=size,
            filters=filters,
            order_by="id",
            descending=False
        )
        # 转换为输出模型
        result["data"] = [TeacherOut.model_validate(item) for item in result["data"]]
        return result
    
    async def get_teacher_by_no(self, db: AsyncSession, teacher_no: int) -> Optional[Teacher]:
        """按教师编号查询"""
        return await self.repo.get_by_no(db, no=teacher_no, no_field="teacher_no")
    
    async def get_teacher_by_id(self, db: AsyncSession, teacher_id: int) -> Optional[TeacherOut]:
        """按教师ID查询"""
        teacher = await self.repo.get(db, teacher_id)
        if not teacher:
            return None
        return TeacherOut.model_validate(teacher)
    
    async def create_teacher(self, db: AsyncSession, teacher_in: TeacherCreate) -> Teacher:
        """创建教师"""
        # 业务逻辑：性别转换（中文->代码）
        if teacher_in.gender == "男":
            teacher_in.gender = 'M'
        elif teacher_in.gender == '女':
            teacher_in.gender = 'F'
        
        return await self.repo.create(db, obj_in=teacher_in)
    
    async def update_teacher(
        self, 
        db: AsyncSession, 
        teacher_id: int, 
        teacher_in: TeacherUpdate
    ) -> Teacher:
        """更新教师信息"""
        teacher = await self.repo.get(db, teacher_id)
        if not teacher:
            raise ValueError("未找到该教师")
        
        # 业务逻辑：性别转换
        update_data = teacher_in.model_dump(exclude_unset=True)
        if "gender" in update_data:
            if update_data["gender"] == "男":
                update_data["gender"] = 'M'
            elif update_data["gender"] == '女':
                update_data["gender"] = 'F'
        
        return await self.repo.update(db, db_obj=teacher, obj_in=update_data)
    
    async def delete_teacher(self, db: AsyncSession, teacher_id: int) -> bool:
        """删除教师"""
        return await self.repo.remove(db, id=teacher_id)


# 创建单例实例
teacher_service = TeacherService()
