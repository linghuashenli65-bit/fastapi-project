from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.repositories.class_repo import class_repo
from backend.schemas.Class import ClassCreate, ClassUpdate
from backend.models.class_ import Class


class ClassService:
    """班级业务逻辑层"""
    
    def __init__(self):
        self.repo = class_repo
    
    async def get_paginated_classes(
        self, 
        db: AsyncSession, 
        page: int = 1, 
        size: int = 10,
        name: Optional[str] = None
    ) -> dict:
        """分页获取班级列表"""
        skip = (page - 1) * size
        count = await self.repo.count(db, name=name)
        lst = await self.repo.get_all(db, skip=skip, limit=size, name=name)
        return {"count": count, "data": lst}
    
    async def create_class(self, db: AsyncSession, class_in: ClassCreate) -> Class:
        """创建班级"""
        return await self.repo.create(db, obj_in=class_in)
    
    async def update_class(
        self, 
        db: AsyncSession, 
        class_id: int, 
        class_in: ClassUpdate
    ) -> Class:
        """更新班级信息"""
        new_class = await self.repo.get(db, id=class_id)
        if not new_class:
            raise ValueError("未找到该班级")
        
        return await self.repo.update(db, db_obj=new_class, obj_in=class_in)
    
    async def delete_class(self, db: AsyncSession, class_id: int) -> bool:
        """删除班级"""
        return await self.repo.remove(db, class_id)
    
    async def get_class_members(self, db: AsyncSession, class_no: str) -> list:
        """获取班级内部学生和教师信息"""
        lst = await self.repo.get_student(class_no, db)
        if not lst:
            raise ValueError("班级不存在")
        return lst


# 创建单例实例
class_service = ClassService()
