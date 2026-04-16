from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class ScoreBase(BaseModel):
    student_no: str = Field(..., description="学号")
    class_no: str = Field(..., description="班级编号")
    start_date: Optional[date] = Field(None, description="进入日期")
    exam_sequence: int = Field(..., description="考核序次")
    exam_date: date = Field(..., description="考试日期")
    score: float = Field(..., ge=0, le=100, description="成绩（0-100分）")


class ScoreCreate(ScoreBase):
    pass


class ScoreUpdate(BaseModel):
    student_no: Optional[str] = None
    class_no: Optional[str] = None
    start_date: Optional[date] = None
    exam_sequence: Optional[int] = None
    exam_date: Optional[date] = None
    score: Optional[float] = Field(None, ge=0, le=100)


class ScoreInDB(ScoreBase):
    id: int
    deleted_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScoreOut(ScoreBase):
    id: int

    class Config:
        from_attributes = True


class ScoreWithInfo(ScoreOut):
    """带学生和班级信息的成绩输出"""
    student_name: Optional[str] = None
    class_name: Optional[str] = None

    class Config:
        from_attributes = True


class ScoreStatistics(BaseModel):
    """成绩统计"""
    total_count: int
    average_score: float
    highest_score: float
    lowest_score: float
    pass_count: int
    pass_rate: float


class ScoreByStudent(BaseModel):
    """按学生统计"""
    student_no: str
    student_name: Optional[str] = None
    class_name: Optional[str] = None
    exam_count: int
    average_score: float
    highest_score: float
    lowest_score: float
