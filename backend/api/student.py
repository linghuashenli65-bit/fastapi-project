from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_async_db
from backend.crud.student_crud import  student_crud
from backend.schemas.student import StudentCreate, StudentUpdate, StudentInDB, StudentOut

router = APIRouter()

@router.get("/",response_model=dict,summary="分页获得学生列表，按学生姓名模糊查找（可选）")
async def get_student(page:int=1,size:int=10,name:str=None,db:AsyncSession=Depends(get_async_db)):
    filters = {}
    if name:
        filters["name"] = f"%{name}%"
    result  = await student_crud.paginate(
        db,
        page=page,
        page_size=size,
        filters=filters,
        order_by="created_at",
        descending=True
    )
    # 将 ORM 对象列表转换为 Pydantic schema 列表
    result["data"] = [StudentOut.model_validate(item) for item in result["data"]]
    return result

@router.post("/",response_model=StudentInDB,summary="创建学生")
async def create_student(student_in:StudentCreate,db:AsyncSession=Depends(get_async_db)):
    return await student_crud.create(db,obj_in=student_in)

@router.put("/{student_no}",response_model=StudentInDB,summary="修改学生信息")
async def update_student(student_no:str,student_in:StudentUpdate,db:AsyncSession=Depends(get_async_db)):
    student = await student_crud.get_by_student_no(db, student_no)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return await student_crud.update(db, db_obj=student, obj_in=student_in)

@router.delete("/{student_no}")
async def delete_student(student_no:str,db:AsyncSession=Depends(get_async_db)):
    student = await student_crud.get_by_student_no(db, student_no)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    await student_crud.delete(db, db_obj=student)
    return {"message":"删除成功"}

@router.get("/{student_no}", response_model=StudentInDB)
async def get_student(
    student_no: str,
    db: AsyncSession = Depends(get_async_db)
):
    student = await student_crud.get_by_student_no(db, student_no)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

