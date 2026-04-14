from types import new_class

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_async_db
from backend.crud.class_crud import class_crud
from backend.schemas.Class import ClassInDB, ClassUpdate, ClassCreate

router = APIRouter()

@router.get("/",response_model=list,summary="分页获得班级列表，按班级姓名模糊查找（可选）")
async def get_class(db:AsyncSession=Depends(get_async_db),skip: int = 0, limit: int = 100):
    lst=await class_crud.get_all(db,skip=skip,limit=limit)
    return lst

@router.post("/",response_model=ClassCreate,summary="创建新班级")
async def create_class(
    new_class: ClassCreate,
    db:AsyncSession=Depends(get_async_db)
):
    try:
        new_class = await class_crud.create(db, db_obj=new_class)
        return new_class
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))

@router.put("/{class_id}/",response_model=ClassUpdate,summary="修改班级信息")
async def update_class(
        class_id:int,
        class_in: ClassUpdate,
        db:AsyncSession=Depends(get_async_db),
):
    new_class=await class_crud.get(db,id=class_id)
    if not new_class:
        raise HTTPException(status_code=400,detail="未找到该班级")
    return await class_crud.update(db, db_obj=new_class, obj_in=class_in)

@router.delete("/{class_id}/",summary="删除班级")
async def delete_class(class_id:int,db:AsyncSession=Depends(get_async_db)):
    return await class_crud.remove(db,class_id)

@router.get("/{class_no}/",response_model=list,summary="查看班级内部学生信息与教师信息")
async def get_class_all(class_no:str,db:AsyncSession=Depends(get_async_db)):
    lis=await class_crud.get_student(class_no,db)
    if not lis:
        raise HTTPException(status_code=404,detail="班级不存在")
    return lis