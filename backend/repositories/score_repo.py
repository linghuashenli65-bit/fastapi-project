from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from typing import Dict, Any, Optional
from backend.models.score import Score
from backend.models.student import Student
from backend.models.class_ import Class
from backend.repositories.base import BaseCRUD
from backend.schemas.score import ScoreCreate, ScoreUpdate


class ScoreRepo(BaseCRUD[Score, ScoreCreate, ScoreUpdate]):
    def __init__(self):
        super().__init__(Score)

    async def get_scores_with_info(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取成绩列表（带学生和班级信息）"""
        from sqlalchemy import cast, String

        query = (
            select(
                Score,
                Student.name.label("student_name"),
                Class.class_name
            )
            .join(Student, Score.student_no == cast(Student.student_no, String))
            .join(Class, Score.class_no == Class.class_no)
            .order_by(Score.exam_date.desc())
        )

        # 获取总数
        count_query = select(func.count()).select_from(
            select(Score).join(Student, Score.student_no == cast(Student.student_no, String))
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页
        skip = (page - 1) * page_size
        query = query.offset(skip).limit(page_size)
        result = await db.execute(query)

        data = []
        for score, student_name, class_name in result:
            item = {
                "id": score.id,
                "student_no": score.student_no,
                "class_no": score.class_no,
                "start_date": score.start_date,
                "exam_sequence": score.exam_sequence,
                "exam_date": score.exam_date,
                "score": float(score.score),
                "student_name": student_name,
                "class_name": class_name,
                "created_at": score.created_at,
                "updated_at": score.updated_at
            }
            data.append(item)

        return {"count": total, "data": data}

    async def get_by_student_no(
        self,
        db: AsyncSession,
        student_no: str,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取学生的成绩列表"""
        from sqlalchemy import cast, String

        query = (
            select(
                Score,
                Student.name.label("student_name"),
                Class.class_name
            )
            .join(Student, Score.student_no == cast(Student.student_no, String))
            .join(Class, Score.class_no == Class.class_no)
            .where(Score.student_no == student_no)
            .order_by(Score.exam_date.desc())
        )

        # 获取总数
        count_query = select(func.count()).select_from(
            query.subquery()
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页
        skip = (page - 1) * page_size
        query = query.offset(skip).limit(page_size)
        result = await db.execute(query)

        data = []
        for score, student_name, class_name in result:
            item = {
                "id": score.id,
                "student_no": score.student_no,
                "class_no": score.class_no,
                "start_date": score.start_date,
                "exam_sequence": score.exam_sequence,
                "exam_date": score.exam_date,
                "score": float(score.score),
                "student_name": student_name,
                "class_name": class_name,
                "created_at": score.created_at,
                "updated_at": score.updated_at
            }
            data.append(item)

        return {"count": total, "data": data}

    async def get_by_class_no(
        self,
        db: AsyncSession,
        class_no: str,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取班级的成绩列表"""
        from sqlalchemy import cast, String

        query = (
            select(
                Score,
                Student.name.label("student_name"),
                Class.class_name
            )
            .join(Student, Score.student_no == cast(Student.student_no, String))
            .join(Class, Score.class_no == Class.class_no)
            .where(Score.class_no == class_no)
            .order_by(Score.exam_date.desc(), Score.student_no)
        )

        # 获取总数
        count_query = select(func.count()).select_from(
            query.subquery()
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页
        skip = (page - 1) * page_size
        query = query.offset(skip).limit(page_size)
        result = await db.execute(query)

        data = []
        for score, student_name, class_name in result:
            item = {
                "id": score.id,
                "student_no": score.student_no,
                "class_no": score.class_no,
                "start_date": score.start_date,
                "exam_sequence": score.exam_sequence,
                "exam_date": score.exam_date,
                "score": float(score.score),
                "student_name": student_name,
                "class_name": class_name,
                "created_at": score.created_at,
                "updated_at": score.updated_at
            }
            data.append(item)

        return {"count": total, "data": data}

    async def get_class_statistics(
        self,
        db: AsyncSession,
        class_no: str
    ) -> Dict[str, Any]:
        """获取班级成绩统计"""
        query = (
            select(
                func.count(Score.id).label("total_count"),
                func.avg(Score.score).label("average_score"),
                func.max(Score.score).label("highest_score"),
                func.min(Score.score).label("lowest_score"),
                func.sum(case((Score.score >= 60, 1), else_=0)).label("pass_count")
            )
            .where(Score.class_no == class_no)
        )

        result = await db.execute(query)
        row = result.one()

        total_count = row.total_count or 0
        pass_count = row.pass_count or 0
        pass_rate = (pass_count / total_count * 100) if total_count > 0 else 0

        return {
            "total_count": total_count,
            "average_score": round(float(row.average_score or 0), 2),
            "highest_score": float(row.highest_score or 0),
            "lowest_score": float(row.lowest_score or 0),
            "pass_count": pass_count,
            "pass_rate": round(pass_rate, 2)
        }

    async def get_student_statistics(
        self,
        db: AsyncSession,
        student_no: str
    ) -> Dict[str, Any]:
        """获取学生成绩统计"""
        query = (
            select(
                func.count(Score.id).label("total_count"),
                func.avg(Score.score).label("average_score"),
                func.max(Score.score).label("highest_score"),
                func.min(Score.score).label("lowest_score"),
                func.sum(case((Score.score >= 60, 1), else_=0)).label("pass_count")
            )
            .where(Score.student_no == student_no)
        )

        result = await db.execute(query)
        row = result.one()

        total_count = row.total_count or 0
        pass_count = row.pass_count or 0
        pass_rate = (pass_count / total_count * 100) if total_count > 0 else 0

        return {
            "total_count": total_count,
            "average_score": round(float(row.average_score or 0), 2),
            "highest_score": float(row.highest_score or 0),
            "lowest_score": float(row.lowest_score or 0),
            "pass_count": pass_count,
            "pass_rate": round(pass_rate, 2)
        }


score_repo = ScoreRepo()
