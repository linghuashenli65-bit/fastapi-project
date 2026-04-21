from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional

class Teacher(BaseModel):
    name: str
    gender: str=None
    phone: str=None
    title: str=None

class TeacherInDB(Teacher):
    id:int
    teacher_no: int
    class Config:
        from_attributes = True

class TeacherCreate(Teacher):
    pass
class TeacherUpdate(Teacher):
    name: Optional[str]=None

class TeacherOut(BaseModel):
    id: int
    teacher_no: int
    name: str
    gender: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    class Config:
        from_attributes = True