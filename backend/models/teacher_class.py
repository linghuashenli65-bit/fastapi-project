from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from datetime import datetime
from backend.core.database import Base

class Teacher_Class(Base):
    __tablename__ = 'teacher_class'
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_no = Column(Integer, ForeignKey('teacher.teacher_no', ondelete='CASCADE'), comment='教师编号')
    class_no = Column(Integer, ForeignKey('class.class_no', ondelete='CASCADE'), comment='班级编号')
    role = Column(String(50), comment='角色，如：班主任、任课老师')
    join_date = Column(DateTime, server_default=func.now(), comment='加入班级日期')
    deleted_at = Column(DateTime, nullable=False, default=datetime(1900, 1, 1, 0, 0, 0))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
