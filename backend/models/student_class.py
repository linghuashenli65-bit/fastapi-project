from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
from backend.core.database import Base

class Student_Class(Base):
    __tablename__ = 'student_class'
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_no = Column(Integer, ForeignKey('student.student_no', ondelete='CASCADE'), comment='学号')
    class_no = Column(Integer, ForeignKey('class.class_no', ondelete='CASCADE'), comment='班级编号')
    is_current = Column(Integer, default=1, comment='是否当前班级，1-是，0-否')
    join_date = Column(DateTime, server_default=func.now(), comment='加入班级日期')
    deleted_at = Column(DateTime, nullable=False, default=datetime(1900, 1, 1, 0, 0, 0))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
