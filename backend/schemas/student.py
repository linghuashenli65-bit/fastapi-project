from pydantic import BaseModel, Field, validator, field_serializer
from datetime import date, datetime
from typing import Optional

class StudentBase(BaseModel):
    name: str
    gender: Optional[str] = Field(None, pattern="^[MF]$")
    birth_date: Optional[date] = None
    birthplace: Optional[str] = None
    graduated_school: Optional[str] = None
    major: Optional[str] = None
    enrollment_date: date
    graduation_date: Optional[date] = None
    education: Optional[int] = Field(None, ge=1, le=5)
    consultant_no: Optional[str] = None

class StudentCreate(StudentBase):
    # 创建时不需要提供 student_no，由后端自动生成
    pass

class StudentUpdate(StudentBase):
    # 所有字段可选
    name: Optional[str] = None
    enrollment_date: Optional[date] = None

class StudentInDB(StudentBase):
    id: int
    student_no: str
    deleted_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StudentOut(BaseModel):
    id: int
    student_no: str
    name: str
    gender: Optional[str] = Field(None, pattern="^[MF]$")
    birth_date: Optional[date] = None
    birthplace: Optional[str] = None
    graduated_school: Optional[str] = None
    major: Optional[str] = None
    enrollment_date: date
    graduation_date: Optional[date] = None
    education: Optional[int] = Field(None, ge=1, le=5)
    consultant_no: Optional[str] = None

    @field_serializer('education')
    def serialize_education(self, value: int) -> str:
        """将 education 代码映射为中文"""
        mapping = {
            1: "高中",
            2: "大专",
            3: "本科",
            4: "硕士",
            5: "博士"
        }
        return mapping.get(value, "未知")

    @field_serializer('gender')
    def serialize_gender(self, value: str) -> str:
        mapping = {
            "M":"男",
            "F":"女"
        }
        return mapping.get(value, "M")

    class Config:
        from_attributes = True