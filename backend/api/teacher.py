from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_async_db
from backend.crud.teacher_crud import teacher_CRUD
from backend.model.teacher import Teacher
from backend.schemas.teacher import TeacherInDB, TeacherOut

router = APIRouter()

@router.get("/",response_model=dict,summary="分页获得教师列表，按学生姓名模糊查找（可选）")
async def get_teacher(page:int=1,size:int=10,name:str=None,db:AsyncSession=Depends(get_async_db)):
    filters = {}
    if name:
        filters["name"] = f"%{name}%"
    result  = await teacher_CRUD.paginate(
        db,
        page=page,
        page_size=size,
        filters=filters,
        order_by="created_at",
        descending=True
    )
    # 将 ORM 对象列表转换为 Pydantic schema 列表
    result["data"] = [TeacherOut.model_validate(item) for item in result["data"]]
    return result
