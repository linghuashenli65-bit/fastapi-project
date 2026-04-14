from fastapi import HTTPException

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_async_db
from backend.crud.teacher_crud import teacher_CRUD
from backend.schemas.teacher import TeacherInDB, TeacherOut, TeacherCreate, TeacherUpdate

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
@router.get("/{teacher_no}/",summary="按教师编号查询教师")
async def get_teacher(teacher_no:int,db:AsyncSession=Depends(get_async_db)):
    teacher = await teacher_CRUD.get_by_no(db,id=teacher_no)
    if not teacher:
        raise HTTPException(status_code=404, detail="未找到该教师")
    return teacher
@router.get("/{teacher_id}/",summary="按教师id查询教师")
async def get_teacher(teacher_id:int,db:AsyncSession=Depends(get_async_db)):
    teacher = await teacher_CRUD.get(db,teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="未找到该教师")
    return TeacherOut.model_validate(teacher)

@router.put("/{teacher_id}/",response_model=TeacherInDB,summary="修改教师信息")
async def create_teacher(teacher_id:int,teacher_in:TeacherCreate,db:AsyncSession=Depends(get_async_db)):
    teacher = await teacher_CRUD.get(db,id=teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="未找到该教师")
    return await teacher_CRUD.update(db, db_obj=teacher, obj_in=teacher_in)

@router.post("/",response_model=TeacherCreate,summary="添加新教师")
async def update_teacher(teacher_in:TeacherUpdate,db:AsyncSession=Depends(get_async_db)):
    try:
        if teacher_in.gender=="男":
            teacher_in.gender='M'
        elif teacher_in.gender=='女':
            teacher_in.gender='F'
        teacher=await teacher_CRUD.update(db, db_obj=teacher_in)
    except Exception as err:
        raise HTTPException(status_code=400,detail=str(err))
    return teacher

@router.delete("/{teacher_id}/",summary="删除教师")
async def delete_teacher(teacher_id:int,db:AsyncSession=Depends(get_async_db)):
    return await teacher_CRUD.remove(db, id=teacher_id)

