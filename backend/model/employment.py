from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint, ForeignKey
from sqlalchemy import Date, SmallInteger
from sqlalchemy.sql import func
from datetime import datetime
from backend.core.database import Base

class Employment(Base):
    __tablename__ = 'employment'
    id=Column(Integer,primary_key=True, autoincrement=True)
    student_no=Column(String(100),ForeignKey("student.student_no",ondelete="SET NULL"))
    company_name=Column(String(100),comment="公司名称")
    job_title=Column(String(100),comment="职位名称")
    salary=Column(Integer,CheckConstraint("salary>0"),comment="岗位工资，单位k")
    offer_date=Column(Date,default=func.now(),comment="offer发放日期")
    employment_start_date=Column(Date,default=None,comment="到岗日期")
    record_type=Column(String(100),CheckConstraint("record_type IN ('offer','employment')"),comment="类型")
    is_current=Column(Integer,CheckConstraint("is_current IN ('1','0')"),comment="是否为当前就业")
    created_at=Column(DateTime,default=func.now())
    updated_at=Column(DateTime,default=func.now(),onupdate=func.now())
    deleted_at=Column(DateTime,default=datetime(1900, 1, 1, 0, 0, 0),onupdate=func.now())