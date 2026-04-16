from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.crud.base import BaseCRUD
from backend.model.Class import Class
from backend.model.student import Student
from backend.model.student_class import Student_Class
from backend.model.teacher import Teacher
from backend.model.teacher_class import Teacher_Class
from backend.schemas.Class import ClassCreate,ClassUpdate

class Class_crud(BaseCRUD[Class,ClassCreate,ClassUpdate]):
    def __init__(self):
        super().__init__(Class)

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100):
        # 子查询：统计每个班级的当前学生人数
        student_count_subq = select(
            Student_Class.class_no,
            func.count(Student_Class.student_no).label('student_count')
        ).join(
            Student, Student_Class.student_no == Student.student_no
        ).where(
            Student_Class.is_current == 1,
            Student.deleted_at == '1900-01-01 00:00:00'
        ).group_by(Student_Class.class_no).subquery()

        # 主查询
        stmt = select(
            Class,
            func.coalesce(student_count_subq.c.student_count, 0).label('student_count')
        ).outerjoin(
            student_count_subq, Class.class_no == student_count_subq.c.class_no
        ).where(
            Class.deleted_at == '1900-01-01 00:00:00'
        ).offset(skip).limit(limit)

        result = await db.execute(stmt)
        rows = result.all()
        class_list = []
        for cls, count in rows:
            class_list.append({
                "class_no": cls.class_no,
                "class_name": cls.class_name,
                "start_date": cls.start_date,
                "student_count": count,
            })

        return class_list

    @staticmethod
    async def get_student( class_no: int, db: AsyncSession):
        # 1. 查询班级是否存在（这里使用异步 select）
        stmt_cls = select(Class).where(Class.class_no == class_no, Class.deleted_at == '1900-01-01 00:00:00')
        result = await db.execute(stmt_cls)
        cls = result.scalar_one_or_none()
        if not cls:
            return None

        # 2. 查询该班级的当前学生列表（通过 student_class 关联）
        stmt_students = select(Student).join(
            Student_Class, Student.student_no == Student_Class.student_no
        ).where(
            Student_Class.class_no == cls.class_no,
            Student_Class.is_current == 1,
            Student.deleted_at == '1900-01-01 00:00:00'
        )
        students_result = await db.execute(stmt_students)
        students = students_result.scalars().all()

        # 3. 查询该班级的教师列表（通过 teacher_class 关联）
        stmt_teachers = select(Teacher).join(
            Teacher_Class, Teacher.teacher_no == Teacher_Class.teacher_no
        ).where(
            Teacher_Class.class_no == class_no,
            Teacher.deleted_at == '1900-01-01 00:00:00'
        )
        teachers_result = await db.execute(stmt_teachers)
        teachers = teachers_result.scalars().all()

        # 4. 合并数据，添加角色字段
        members = []
        for s in students:
            members.append({
                "name": s.name,
                "code": s.student_no,
                "role": "学生",
                "gender": s.gender,
                "phone": "",  # 学生可能没有电话字段，如果有则取 s.phone
                "title": "",
                "major": s.major,
            })
        for t in teachers:
            members.append({
                "name": t.name,
                "code": t.teacher_no,
                "role": "教师",
                "gender": t.gender,
                "phone": t.phone,
                "title": getattr(t, 'title', ''),
                "major": "",
            })
        return members

class_crud=Class_crud()


