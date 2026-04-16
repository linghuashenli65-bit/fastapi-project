# 项目重构迁移指南

## 重构完成情况 ✅

本次重构已将项目调整为符合MVC模式的分层架构。

## 新的项目结构

```
backend/
├── app/                    # 应用入口
│   └── main.py            # FastAPI应用主文件（已更新import）
├── core/                   # 核心配置
│   ├── config.py
│   ├── database.py
│   └── settings.py
├── models/                 # ⭐ Model层（原model/，已重命名）
│   ├── __init__.py
│   ├── agent.py           # AI相关模型
│   ├── class_.py          # 班级模型（已重命名，避免关键字）
│   ├── dashboard.py       # 仪表板模型
│   ├── employment.py      # 就业模型
│   ├── llm.py             # LLM接口
│   ├── student.py         # 学生模型
│   ├── student_class.py   # 学生-班级关联
│   ├── teacher.py         # 教师模型
│   └── teacher_class.py   # 教师-班级关联
├── schemas/                # 数据传输对象（DTO）
│   ├── agent.py
│   ├── Class.py
│   ├── employment.py
│   ├── student.py
│   └── teacher.py
├── repositories/          # ⭐ Repository层（原crud/，已重命名）
│   ├── __init__.py
│   ├── base.py            # 基础CRUD类
│   ├── class_repo.py      # 班级数据访问
│   ├── employment_repo.py # 就业数据访问
│   ├── sql_service.py     # SQL执行服务
│   ├── student_repo.py    # 学生数据访问
│   └── teacher_repo.py    # 教师数据访问
├── services/              # ⭐ Service层（新增业务逻辑层）
│   ├── __init__.py
│   ├── class_service.py   # 班级业务逻辑
│   ├── employment_service.py # 就业业务逻辑
│   ├── student_service.py # 学生业务逻辑
│   └── teacher_service.py # 教师业务逻辑
├── api/                    # API层（已重构）
│   ├── agent.py           # AI模块API（已更新import）
│   ├── class_student.py   # 班级模块API（已重构）
│   ├── employment.py      # 就业模块API（已重构）
│   ├── student.py         # 学生模块API（已重构）
│   └── teacher.py         # 教师模块API（已重构）
├── utils/                  # 工具函数
│   └── helpers.py
├── static/                 # 静态文件（View层）
└── REFACTORING.md         # 详细重构说明文档
```

## 关键变更说明

### 1. 目录重命名
- `model/` → `models/`（小写复数）
- `crud/` → `repositories/`（更符合语义）
- `model/Class.py` → `models/class_.py`（避免Python关键字）

### 2. 新增Service层
所有业务逻辑已从API层迁移到Service层：

**示例：教师模块**
- `services/teacher_service.py` - 处理教师相关业务逻辑
  - 性别转换（中文"男/女" → 代码"M/F"）
  - 统一的CRUD操作
  - 业务异常处理

### 3. API层简化
API层现在只负责：
- HTTP请求处理
- 参数验证
- 响应格式化
- 调用Service层

**示例对比**：

**重构前**：
```python
@router.post("/")
async def create_teacher(teacher_in: TeacherCreate, db: AsyncSession = Depends(get_async_db)):
    # 业务逻辑混在API层
    if teacher_in.gender == "男":
        teacher_in.gender = 'M'
    elif teacher_in.gender == '女':
        teacher_in.gender = 'F'
    return await teacher_crud.create(db, obj_in=teacher_in)
```

**重构后**：
```python
@router.post("/", response_model=TeacherInDB, summary="添加新教师")
async def create_teacher(teacher_in: TeacherCreate, db: AsyncSession = Depends(get_async_db)):
    """创建新教师"""
    try:
        teacher = await teacher_service.create_teacher(db, teacher_in)
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))
    return teacher
```

### 4. 修复的问题

#### ✅ 路由冲突
修复了 `teacher.py` 中的路由冲突：
```python
# 之前：两条路由路径相同
@router.get("/{teacher_no}/", ...)  # 冲突
@router.get("/{teacher_id}/", ...)  # 冲突

# 现在：使用不同的路径前缀
@router.get("/no/{teacher_no}", ...)
@router.get("/{teacher_id}", ...)
```

#### ✅ 命名不规范
- 统一使用小写目录名
- 统一使用 `{entity}_service.py` 命名
- 统一使用 `{entity}_repo.py` 命名

#### ✅ Import路径更新
所有文件的import路径已更新：
```python
# 旧路径
from backend.model.xxx import Xxx
from backend.crud.xxx import xxx_crud

# 新路径
from backend.models.xxx import Xxx
from backend.repositories.xxx import xxx_repo
from backend.services.xxx import xxx_service
```

## 如何使用新架构

### 开发新功能步骤

#### 1. 定义Model（如需要）
在 `models/` 目录下创建数据模型：
```python
# models/user.py
from sqlalchemy import Column, Integer, String
from backend.core.database import Base

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
```

#### 2. 定义Schema
在 `schemas/` 目录下创建DTO：
```python
# schemas/user.py
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str

class UserOut(BaseModel):
    id: int
    name: str
```

#### 3. 创建Repository
在 `repositories/` 目录下创建数据访问层：
```python
# repositories/user_repo.py
from backend.repositories.base import BaseCRUD
from backend.models.user import User
from backend.schemas.user import UserCreate, UserUpdate

class UserRepo(BaseCRUD[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

user_repo = UserRepo()
```

#### 4. 创建Service
在 `services/` 目录下创建业务逻辑层：
```python
# services/user_service.py
class UserService:
    def __init__(self):
        self.repo = user_repo
    
    async def create_user(self, db, user_in):
        # 业务逻辑
        return await self.repo.create(db, obj_in=user_in)

user_service = UserService()
```

#### 5. 创建API
在 `api/` 目录下创建API路由：
```python
# api/user.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_async_db
from backend.services.user_service import user_service
from backend.schemas.user import UserCreate, UserOut

router = APIRouter()

@router.post("/", response_model=UserOut)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_async_db)):
    return await user_service.create_user(db, user_in)
```

#### 6. 注册路由
在 `app/main.py` 中注册路由：
```python
from backend.api import user
app.include_router(user.router, prefix="/user", tags=["用户模块"])
```

## 迁移现有代码

如果你有自定义代码需要迁移到新架构：

1. **更新import路径**：
   ```python
   # 替换所有
   from backend.model.xxx import → from backend.models.xxx import
   from backend.crud.xxx import → from backend.repositories.xxx import
   ```

2. **提取业务逻辑到Service层**：
   - 将API层中的业务逻辑移到对应的Service文件
   - API层只保留HTTP处理逻辑

3. **使用新的命名规范**：
   - Repository: `{entity}_repo.py`
   - Service: `{entity}_service.py`

## 优势总结

### 1. 职责分离
- **API层**：HTTP处理
- **Service层**：业务逻辑
- **Repository层**：数据访问

### 2. 易于测试
- 每层可独立测试
- 便于mock和单元测试

### 3. 代码复用
- Service层逻辑可被多个API调用
- Repository层可被多个Service调用

### 4. 易于维护
- 修改业务逻辑只需修改Service层
- 修改数据访问只需修改Repository层
- 修改API接口只需修改API层

## 注意事项

1. **不要跨层调用**：
   - ❌ API层不能直接调用Repository层
   - ❌ Repository层不能调用Service层
   - ✅ 正确流程：API → Service → Repository

2. **事务管理**：
   - 事务应该在Service层或API层控制
   - Repository层不负责事务管理

3. **异常处理**：
   - Repository层抛出技术异常
   - Service层转换为业务异常
   - API层转换为HTTP错误响应

## 文档参考

- `REFACTORING.md` - 详细的MVC重构说明
- `backend/README.md` - 项目说明文档

## 后续优化建议

1. **添加单元测试**：为每一层添加对应的单元测试
2. **添加API文档**：使用OpenAPI/Swagger生成API文档
3. **添加日志系统**：在每一层添加适当的日志记录
4. **性能优化**：考虑添加缓存层（Redis）
5. **权限控制**：添加认证和授权中间件
