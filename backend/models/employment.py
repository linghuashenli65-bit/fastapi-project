from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint, ForeignKey, Float
from sqlalchemy.sql import func
from datetime import datetime
from backend.core.database import Base

class Employment(Base):
    __tablename__ = 'employment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_no = Column(Integer, ForeignKey('student.student_no', ondelete='SET NULL'), nullable=True, comment='学号')
    company_name = Column(String(255), comment='公司名称')
    position = Column(String(255), comment='职位')
    salary = Column(Float, comment='薪资')
    employment_date = Column(DateTime, comment='就业日期')
    deleted_at = Column(DateTime, nullable=False, default=datetime(1900, 1, 1, 0, 0, 0))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
