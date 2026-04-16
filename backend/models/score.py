from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Numeric
from sqlalchemy.sql import func
from datetime import datetime
from backend.core.database import Base


class Score(Base):
    __tablename__ = "score"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    student_no = Column(String(50), ForeignKey("student.student_no", ondelete="CASCADE"), comment="学号")
    class_no = Column(String(50), ForeignKey("class.class_no", ondelete="CASCADE"), comment="班级编号")
    start_date = Column(Date, comment="进入日期")
    exam_sequence = Column(Integer, comment="考核序次")
    exam_date = Column(Date, comment="考试日期")
    score = Column(Numeric(5, 2), comment="成绩")
    deleted_at = Column(DateTime, nullable=False, default=datetime(1900, 1, 1, 0, 0, 0))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
