from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
DEFAULT_NOT_DELETED_TIME = datetime(1900, 1, 1, 0, 0, 0)

class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
        # 软删除字段名，默认 "deleted_at"，如果模型使用其他名称可传入
        self.soft_delete_field = getattr(model, "deleted_at", None)

    def _apply_soft_delete_filter(self, stmt, include_deleted: bool = False):
        """自动添加软删除过滤条件（默认排除已删除记录）"""
        if include_deleted:
            return stmt
        if self.soft_delete_field is not None:
            # 假设 deleted_at 为 NULL 表示未删除
            return stmt.where(self.soft_delete_field==DEFAULT_NOT_DELETED_TIME)
        return stmt

    async def get(self, db: AsyncSession, id: Any, include_deleted: bool = False) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_no(self, db: AsyncSession, no: str, no_field: str = "no", include_deleted: bool = False) -> Optional[ModelType]:
        column = getattr(self.model, no_field, None)
        if column is None:
            raise AttributeError(f"Model {self.model.__name__} has no attribute {no_field}")
        stmt = select(self.model).where(column == no)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        descending: bool = False,
        include_deleted: bool = False
    ) -> List[ModelType]:
        stmt = select(self.model)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted)

        if filters:
            for key, value in filters.items():
                column = getattr(self.model, key, None)
                if column is not None:
                    if isinstance(value, str) and "%" in value:
                        stmt = stmt.where(column.like(value))
                    else:
                        stmt = stmt.where(column == value)

        if order_by:
            column = getattr(self.model, order_by)
            if descending:
                stmt = stmt.order_by(column.desc())
            else:
                stmt = stmt.order_by(column.asc())

        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def count(self, db: AsyncSession, filters: Optional[Dict[str, Any]] = None, include_deleted: bool = False) -> int:
        stmt = select(func.count()).select_from(self.model)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted)
        if filters:
            for key, value in filters.items():
                column = getattr(self.model, key)
                if isinstance(value, str) and "%" in value:
                    stmt = stmt.where(column.like(value))
                else:
                    stmt = stmt.where(column == value)
        result = await db.execute(stmt)
        return result.scalar_one()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_data = obj_in.model_dump(exclude_unset=True)
        # 确保软删除字段初始为 DEFAULT_NOT_DELETED_TIME（未删除）
        if self.soft_delete_field is not None:
            obj_data.setdefault("deleted_at", DEFAULT_NOT_DELETED_TIME)
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: Any, soft: bool = True) -> Optional[ModelType]:
        """软删除（默认）或物理删除"""
        obj = await self.get(db, id=id, include_deleted=False)  # 只找未删除的
        if not obj:
            return None
        if soft and self.soft_delete_field is not None:
            # 软删除：设置 deleted_at 为当前时间
            setattr(obj, self.soft_delete_field.key, datetime.now())
            db.add(obj)
            await db.commit()
            await db.refresh(obj)
            return obj
        else:
            # 物理删除
            await db.delete(obj)
            await db.commit()
            return obj

    async def hard_remove(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        """强制物理删除（包括已软删除的记录）"""
        obj = await self.get(db, id=id, include_deleted=True)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def restore(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        """恢复已软删除的记录"""
        if self.soft_delete_field is None:
            raise NotImplementedError("Model does not support soft delete")
        obj = await self.get(db, id=id, include_deleted=True)
        if obj and getattr(obj, self.soft_delete_field.key) !=DEFAULT_NOT_DELETED_TIME:
            setattr(obj, self.soft_delete_field.key, DEFAULT_NOT_DELETED_TIME)
            db.add(obj)
            await db.commit()
            await db.refresh(obj)
            return obj
        return None

    async def paginate(
            self,
            db: AsyncSession,
            *,
            page: int = 1,
            page_size: int = 10,
            filters: Optional[Dict[str, Any]] = None,
            order_by: Optional[str] = None,
            descending: bool = False,
            include_deleted: bool = False
    ) -> Dict[str, Any]:
        """
        分页查询，返回字典格式：{"count": 总数, "data": 当前页数据列表}
        """
        skip = (page - 1) * page_size
        items = await self.get_multi(
            db,
            skip=skip,
            limit=page_size,
            filters=filters,
            order_by=order_by,
            descending=descending,
            include_deleted=include_deleted
        )
        total = await self.count(db, filters=filters, include_deleted=include_deleted)
        return {
            "count": total,
            "data": items
        }
