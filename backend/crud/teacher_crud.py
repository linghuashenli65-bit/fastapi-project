from backend.core.database import Base
from backend.crud.base import BaseCRUD
from backend.model.teacher import Teacher
from backend.schemas.teacher import TeacherCreate, TeacherUpdate


class TeacherCRUD(BaseCRUD[Teacher,TeacherCreate,TeacherUpdate]):
    def __init__(self):
        super().__init__(Teacher)

    async def find_by_name(self, db, name, include_deleted=False):
        filters = {"name": name}
        return await self.get_multi(db, filters=filters, include_deleted=include_deleted)

    async def like_by_title(self, db, title: str, include_deleted=False):
        filters = {"title": f"%{title}%"}
        return await self.get_multi(db, filters=filters, include_deleted=include_deleted)


teacher_CRUD = TeacherCRUD()

