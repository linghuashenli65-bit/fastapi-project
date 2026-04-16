from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.repositories.employment_repo import employment_repo
from backend.schemas.employment import EmploymentCreate, EmploymentUpdate, EmploymentOutDB
from backend.model.employment import Employment


class EmploymentService:
    """就业业务逻辑层"""
    
    def __init__(self):
        self.repo = employment_repo
    
    async def get_paginated_employment(
        self, 
        db: AsyncSession, 
        page: int = 1, 
        size: int = 10, 
        company_name: Optional[str] = None
    ) -> dict:
        """分页获取就业信息列表"""
        filters = {}
        if company_name:
            filters["company_name"] = f"%{company_name}%"
        
        result = await self.repo.paginate(
            db,
            page=page,
            page_size=size,
            filters=filters,
            order_by="created_at",
            descending=True
        )
        # 转换为输出模型
        result["data"] = [EmploymentOutDB.model_validate(item) for item in result["data"]]
        return result
    
    async def create_employment(self, db: AsyncSession, employment_in: EmploymentCreate) -> Employment:
        """创建就业信息"""
        return await self.repo.create(db, obj_in=employment_in)
    
    async def update_employment(
        self, 
        db: AsyncSession, 
        employment_id: int, 
        employment_in: EmploymentUpdate
    ) -> Employment:
        """更新就业信息"""
        employment = await self.repo.get(db, employment_id)
        if not employment:
            raise ValueError("未找到该就业信息")
        
        return await self.repo.update(db, db_obj=employment, obj_in=employment_in)
    
    async def delete_employment(self, db: AsyncSession, employment_id: int) -> bool:
        """删除就业信息"""
        employment = await self.repo.get(db, employment_id)
        if not employment:
            raise ValueError("未找到该就业信息")
        
        return await self.repo.remove(db, id=employment_id)


# 创建单例实例
employment_service = EmploymentService()
