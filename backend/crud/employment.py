from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.base import BaseCRUD
from backend.model.employment import Employment
from backend.schemas.employment import EmploymentCreate, EmploymentUpdate
from sqlalchemy import select, func, and_
from backend.model.student import Student

class Employment_crud(BaseCRUD[Employment,EmploymentCreate,EmploymentUpdate]):
    def __init__(self):
        super().__init__(Employment)

    async def paginate(self, db: AsyncSession, page: int = 1, page_size: int = 10,
                       filters: dict = None, order_by: str = "created_at", descending: bool = True):
        # 构建查询
        stmt = select(
            Employment,
            Student.name.label("student_name")
        ).join(Student, Employment.student_no == Student.student_no)

        # 应用过滤
        if filters:
            for key, value in filters.items():
                if key == "company_name" and value.startswith("%"):
                    stmt = stmt.where(Employment.company_name.like(value))
                else:
                    stmt = stmt.where(getattr(Employment, key) == value)

        # 排序
        order_col = getattr(Employment, order_by)
        if descending:
            stmt = stmt.order_by(order_col.desc())
        else:
            stmt = stmt.order_by(order_col.asc())

        # 分页
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        # 执行
        result = await db.execute(stmt)
        rows = result.all()  # 每个元素是 (Employment, student_name)

        # 构建返回数据
        items = []
        for emp, student_name in rows:
            # 将 Employment 对象转换为字典，并添加 student_name
            emp_dict = emp.__dict__.copy()
            emp_dict.pop('_sa_instance_state', None)
            emp_dict['student_name'] = student_name
            items.append(emp_dict)

        # 查询总数（需要单独执行，不含分页）
        count_stmt = select(func.count()).select_from(Employment)
        if filters:
            for key, value in filters.items():
                if key == "company_name" and value.startswith("%"):
                    count_stmt = count_stmt.where(Employment.company_name.like(value))
                else:
                    count_stmt = count_stmt.where(getattr(Employment, key) == value)
        total = await db.scalar(count_stmt)

        pages = (total + page_size - 1) // page_size
        return {"data": items, "count": total, "page": page, "size": page_size, "pages": pages}



employment_crud=Employment_crud()