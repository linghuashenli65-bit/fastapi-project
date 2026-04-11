from backend.crud.base import BaseCRUD
from backend.model.student import Student
from backend.schemas.student import StudentCreate, StudentUpdate

class StudentCRUD(BaseCRUD[Student, StudentCreate, StudentUpdate]):
    def __init__(self):
        super().__init__(Student)

    # 如果需要自定义软删除过滤（因为默认值是 '1900-01-01' 而不是 NULL）
    # 可以重写 _apply_soft_delete_filter 方法，但这里假设基类已处理。

    # 额外添加学生特有的查询方法
    async def get_by_student_no(self, db, student_no: str, include_deleted: bool = False):
        return await self.get_by_no(db, no=student_no, no_field="student_no", include_deleted=include_deleted)

    async def get_by_name_like(self, db, name: str, skip: int = 0, limit: int = 100):
        filters = {"name": f"%{name}%"}
        return await self.get_multi(db, skip=skip, limit=limit, filters=filters)

# 创建单例实例
student_crud = StudentCRUD()