
from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint, ForeignKey
from sqlalchemy import Date, SmallInteger
from sqlalchemy.sql import func
from datetime import datetime
from backend.core.database import Base


class Student(Base):
    __tablename__ = "student"
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_no = Column(Integer, nullable=False, unique=True,comment="学号")
    name = Column(String(100),comment="姓名")
    gender=Column(String(10),CheckConstraint("gender IN ('M','F')"),comment="性别")
    birth_date=Column(Date,comment="出生日期")
    birthplace=Column(String(100),comment="籍贯")
    graduated_school=Column(String(100),comment="毕业学校")
    major=Column(String(100),comment="专业")
    enrollment_date = Column(Date, nullable=False)
    graduation_date = Column(Date)
    education = Column(SmallInteger)  # 学历：1-高中 2-大专 3-本科 4-硕士 5-博士
    consultant_no = Column(String(50), ForeignKey("teacher.teacher_no", ondelete="SET NULL"))
    deleted_at = Column(DateTime, nullable=False, default=datetime(1900, 1, 1, 0, 0, 0))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
