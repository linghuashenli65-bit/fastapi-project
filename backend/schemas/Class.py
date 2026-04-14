from pydantic import BaseModel, Field,field_serializer
from datetime import date, datetime
from typing import Optional

class Class(BaseModel):
    class_name: str
    start_date: Optional[date]

class ClassInDB(BaseModel):
    id:int
    class_no:int
    class Config:
        from_attributes = True

class ClassCreate(Class):
    pass

class ClassUpdate(Class):
    class_name: str | None
    start_date: Optional[date] | None

class ClassOutDB(BaseModel):
    class_no:int
    class_name: str
    start_date: Optional[date]|None
    student_count: int = 0
    class Config:
        from_attributes = True

