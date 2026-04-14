
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from backend.core.database import Base

class Student_Class(Base):
    __tablename__ = 'student_class'
    id = Column(Integer, primary_key=True)
    student_no=Column(Integer,nullable=False,unique=True)
    class_no=Column(Integer,nullable=False,unique=True)
    start_date=Column(DateTime,nullable=False,default=func.now())
    end_date=Column(DateTime,default=func.now())
    is_current=Column(Integer,default=1,comment="是否当前班级")
    reason=Column(String(100),nullable=False,default="normal",comment="变动原因")
    created_at=Column(DateTime,default=func.now())
    updated_at=Column(DateTime,default=func.now(),onupdate=func.now())
    deleted_at=Column(DateTime,default=datetime(1900, 1, 1, 0, 0, 0),onupdate=func.now())

