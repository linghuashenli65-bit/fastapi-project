from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from backend.core.database import Base


class Teacher_Class(Base):
    __tablename__ = 'teacher_class'
    id = Column(Integer, primary_key=True)
    teacher_no = Column(Integer, unique=True)
    class_no = Column(Integer, unique=True)
    role=Column(String(100),comment="教师职称")
    start_date=Column(DateTime,nullable=False,default=func.now())
    end_date=Column(DateTime,default=func.now())
    is_current=Column(Integer,default=1)
    created_at=Column(DateTime,default=func.now())
    updated_at=Column(DateTime,default=func.now(),onupdate=func.now())
    deleted_at=Column(DateTime,default=datetime(1900, 1, 1, 0, 0, 0))
