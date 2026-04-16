from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
from backend.core.database import Base
class Class(Base):
    __tablename__ = 'class'
    id = Column(Integer, primary_key=True)
    class_no=Column(String(100),unique=True,comment="班级编号")
    class_name=Column(String(100),comment="班级名称")
    start_date=Column(DateTime,comment="开班日期")
    deleted_at=Column(DateTime,nullable=False, default=datetime(1900, 1, 1, 0, 0, 0))
    created_at=Column(DateTime,server_default=func.now(),comment="创建日期")
    updated_at=Column(DateTime,server_default=func.now(), onupdate=func.now(),comment="修改日期")
