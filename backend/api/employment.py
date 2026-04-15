
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_async_db
from backend.crud.employment import employment_crud
from backend.schemas.employment import EmploymentCreate, EmploymentUpdate,EmploymentOutDB

router = APIRouter()

@router.get("/",response_model=dict,summary="分页获得就业列表,可以按公司名称筛选")
async def get_employment(page:int=1,size:int=10,company_name:str=None,db: AsyncSession = Depends(get_async_db)):
    filters={}
    if company_name:
        filters["company_name"] = f"%{company_name}%"
    result = await employment_crud.paginate(
        db,
        page=page,
        page_size=size,
        filters=filters,
        order_by="created_at",
        descending=True
    )
    result["data"] = [EmploymentOutDB.model_validate(item) for item in result["data"]]
    return result

@router.post("/",response_model=EmploymentCreate,summary="创建就业信息")
async def create_employment(employment_in:EmploymentCreate,db: AsyncSession = Depends(get_async_db)):
    result = await employment_crud.create(employment_in=employment_in,db=db)
    return result

@router.put("/{id}",response_model=EmploymentUpdate,summary="修改就业信息")
async def update_employment(id:int,employment_in:EmploymentUpdate,db: AsyncSession = Depends(get_async_db)):
    employment=employment_crud.get(id=id,db=db)
    if employment is None:
        raise HTTPException(status_code=404, detail="未找到该就业信息")
    return await employment_crud.update(employment,db=db)

@router.delete("/{id}",summary="删除就业信息")
async def delete_employment(id:int,db: AsyncSession = Depends(get_async_db)):
    employment=employment_crud.get(id=id,db=db)
    if employment is None:
        raise HTTPException(status_code=404, detail="未找到该就业信息")
    return await employment_crud.remove(employment,db=db,id=id)