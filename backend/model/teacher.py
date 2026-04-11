from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint, ForeignKey
from sqlalchemy import Date, SmallInteger
from sqlalchemy.sql import func
from datetime import datetime
from backend.core.database import Base

class Teacher(Base):
    __tablename__ = 'teacher'
    id = Column(Integer, primary_key=True)
    teacher_no=Column(Integer, unique=True,comment="教师编号")
    name=Column(String(100),comment="教师姓名")
    gender=Column(String(10),CheckConstraint("gender IN ('M','F')"),comment="性别")
    phone=Column(String(100),comment="电话号")
    title=Column(String(100),comment="教师职称")
    deleted_at = Column(DateTime, nullable=False, default=datetime(1900, 1, 1, 0, 0, 0))
    created_at = Column(DateTime, nullable=False,default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
