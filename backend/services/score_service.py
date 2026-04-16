from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from backend.repositories.score_repo import score_repo
from backend.schemas.score import ScoreCreate, ScoreUpdate, ScoreOut
from backend.models.score import Score


class ScoreService:
    def __init__(self):
        self.repo = score_repo

    async def get_scores(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10
    ) -> dict:
        """获取成绩列表（分页）"""
        return await self.repo.get_scores_with_info(db, page=page, page_size=page_size)

    async def get_score_by_id(
        self,
        db: AsyncSession,
        score_id: int
    ) -> Optional[dict]:
        """获取单个成绩记录"""
        score = await self.repo.get(db, score_id)
        if not score:
            return None
        return {
            "id": score.id,
            "student_no": score.student_no,
            "class_no": score.class_no,
            "start_date": score.start_date,
            "exam_sequence": score.exam_sequence,
            "exam_date": score.exam_date,
            "score": float(score.score),
            "created_at": score.created_at,
            "updated_at": score.updated_at
        }

    async def get_scores_by_student(
        self,
        db: AsyncSession,
        student_no: str,
        page: int = 1,
        page_size: int = 10
    ) -> dict:
        """获取学生的成绩列表"""
        return await self.repo.get_by_student_no(db, student_no=student_no, page=page, page_size=page_size)

    async def get_scores_by_class(
        self,
        db: AsyncSession,
        class_no: str,
        page: int = 1,
        page_size: int = 10
    ) -> dict:
        """获取班级的成绩列表"""
        return await self.repo.get_by_class_no(db, class_no=class_no, page=page, page_size=page_size)

    async def create_score(
        self,
        db: AsyncSession,
        score_in: ScoreCreate
    ) -> Score:
        """创建成绩记录"""
        # 验证成绩范围
        if not (0 <= score_in.score <= 100):
            raise ValueError("成绩必须在0-100之间")

        return await self.repo.create(db, obj_in=score_in)

    async def update_score(
        self,
        db: AsyncSession,
        score_id: int,
        score_in: ScoreUpdate
    ) -> Score:
        """更新成绩记录"""
        score = await self.repo.get(db, score_id)
        if not score:
            raise ValueError("成绩记录不存在")

        if score_in.score is not None:
            if not (0 <= score_in.score <= 100):
                raise ValueError("成绩必须在0-100之间")

        return await self.repo.update(db, db_obj=score, obj_in=score_in)

    async def delete_score(
        self,
        db: AsyncSession,
        score_id: int
    ) -> bool:
        """删除成绩记录（软删除）"""
        score = await self.repo.get(db, score_id)
        if not score:
            raise ValueError("成绩记录不存在")

        return await self.repo.remove(db, id=score_id, soft=True)

    async def get_class_statistics(
        self,
        db: AsyncSession,
        class_no: str
    ) -> dict:
        """获取班级成绩统计"""
        return await self.repo.get_class_statistics(db, class_no=class_no)

    async def get_student_statistics(
        self,
        db: AsyncSession,
        student_no: str
    ) -> dict:
        """获取学生成绩统计"""
        return await self.repo.get_student_statistics(db, student_no=student_no)


score_service = ScoreService()
