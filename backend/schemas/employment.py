from pydantic import BaseModel, Field,field_serializer
from datetime import date, datetime
from typing import Optional

class Employment(BaseModel):
    student_no:str
    company_name:str
    job_title:str
    salary:int
    offer_date:date
    employment_start_date:date
    record_type:str
    is_current:int



class EmploymentInDB(Employment):
    pass

class EmploymentOutDB(Employment):
    id: int
    student_no: str
    student_name: str
    company_name: str
    job_title: Optional[str] = None
    salary: Optional[int] = None
    offer_date: Optional[date] = None
    employment_start_date: Optional[date] = None
    record_type: Optional[str] = None
    is_current: int
    class Config:
        from_attributes = True

class EmploymentCreate(Employment):
    pass
class EmploymentUpdate(BaseModel):
    student_no: str
    company_name: str|None
    job_title: str|None
    salary: int|None
    offer_date: date|None
    employment_start_date: date|None
    record_type: str|None
    is_current: int|None