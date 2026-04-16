# MVC 模式重构说明

## 重构概述

本次重构将项目调整为更符合MVC（Model-View-Controller）架构的模式，采用分层设计，提高代码的可维护性和可扩展性。

## 目录结构变更

### 新增目录
- `models/` - 数据模型层（原 `model/`）
- `repositories/` - 数据访问层（原 `crud/`）
- `services/` - 业务逻辑层（新增）

### 保留目录
- `api/` - 控制器层（路由和HTTP处理）
- `schemas/` - 数据传输对象（DTO）
- `core/` - 核心配置（数据库、配置等）
- `static/` - 静态文件（View层）

## 分层架构说明

### 1. Models 层（models/）
**职责**：定义数据库表结构和ORM模型

**示例文件**：
- `models/teacher.py` - 教师数据模型
- `models/student.py` - 学生数据模型
- `models/class_.py` - 班级数据模型

**命名规范**：
- 文件名使用小写字母，避免Python关键字（如 `class_.py` 而非 `Class.py`）

### 2. Schemas 层（schemas/）
**职责**：定义数据传输对象（Pydantic模型），用于API输入输出验证

**示例文件**：
- `schemas/teacher.py` - 教师相关的Schema
- `schemas/student.py` - 学生相关的Schema

### 3. Repositories 层（repositories/）
**职责**：数据访问层，封装数据库CRUD操作

**示例文件**：
- `repositories/base.py` - 基础CRUD类
- `repositories/teacher_repo.py` - 教师数据访问
- `repositories/student_repo.py` - 学生数据访问

**特点**：
- 继承自 `BaseCRUD` 提供通用CRUD方法
- 不包含业务逻辑，只负责数据持久化
- 命名规范：`{entity}_repo.py`

### 4. Services 层（services/） ⭐ 新增
**职责**：业务逻辑层，处理复杂的业务规则和逻辑

**示例文件**：
- `services/teacher_service.py` - 教师业务逻辑
- `services/student_service.py` - 学生业务逻辑
- `services/class_service.py` - 班级业务逻辑

**特点**：
- 调用Repository层进行数据访问
- 处理业务逻辑（如性别转换、数据验证等）
- 命名规范：`{entity}_service.py`

### 5. API 层（api/）
**职责**：控制器层，处理HTTP请求和响应

**示例文件**：
- `api/teacher.py` - 教师相关API路由
- `api/student.py` - 学生相关API路由

**职责变化**：
- 之前：直接调用CRUD层，业务逻辑混杂
- 现在：只负责请求参数处理、响应格式化，业务逻辑委托给Service层

## 重构要点

### 1. 命名规范化
- ✅ `model/` → `models/`（小写复数）
- ✅ `crud/` → `repositories/`（更符合语义）
- ✅ `Class.py` → `class_.py`（避免关键字）
- ✅ `teacher_crud.py` → `teacher_repo.py`（统一命名）

### 2. 业务逻辑分离
**重构前**（API层包含业务逻辑）：
```python
@router.post("/")
async def create_teacher(teacher_in: TeacherCreate, db: AsyncSession = Depends(get_async_db)):
    if teacher_in.gender == "男":
        teacher_in.gender = 'M'
    elif teacher_in.gender == '女':
        teacher_in.gender = 'F'
    return await teacher_crud.create(db, obj_in=teacher_in)
```

**重构后**（Service层处理业务逻辑）：
```python
# Service层
async def create_teacher(self, db: AsyncSession, teacher_in: TeacherCreate) -> Teacher:
    if teacher_in.gender == "男":
        teacher_in.gender = 'M'
    elif teacher_in.gender == '女':
        teacher_in.gender = 'F'
    return await self.repo.create(db, obj_in=teacher_in)

# API层
@router.post("/")
async def create_teacher(teacher_in: TeacherCreate, db: AsyncSession = Depends(get_async_db)):
    return await teacher_service.create_teacher(db, teacher_in)
```

### 3. 路由冲突修复
**问题**：teacher.py 中有重复的路由定义
```python
@router.get("/{teacher_no}/", ...)  # 路径冲突
@router.get("/{teacher_id}/", ...)  # 路径冲突
```

**解决**：使用不同的路径前缀
```python
@router.get("/no/{teacher_no}", ...)
@router.get("/{teacher_id}", ...)
```

### 4. Import路径更新
所有文件中的import路径已更新：
- `from backend.model.xxx` → `from backend.models.xxx`
- `from backend.crud.xxx` → `from backend.repositories.xxx`
- 新增 `from backend.services.xxx`

## 优势

### 1. 职责清晰
- **API层**：只负责HTTP请求处理
- **Service层**：专注业务逻辑
- **Repository层**：专注数据访问

### 2. 易于测试
- 每层可以独立测试
- Service层可以mock Repository层
- API层可以mock Service层

### 3. 代码复用
- Service层的逻辑可以被多个API调用
- Repository层可以被多个Service调用

### 4. 易于维护
- 修改业务逻辑只需修改Service层
- 修改数据库操作只需修改Repository层
- 修改API接口只需修改API层

## 使用示例

### 创建新功能时的开发流程

1. **定义Model** (`models/xxx.py`)
```python
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
```

2. **定义Schema** (`schemas/xxx.py`)
```python
class UserCreate(BaseModel):
    name: str

class UserOut(BaseModel):
    id: int
    name: str
```

3. **创建Repository** (`repositories/user_repo.py`)
```python
class UserRepo(BaseCRUD[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

user_repo = UserRepo()
```

4. **创建Service** (`services/user_service.py`)
```python
class UserService:
    def __init__(self):
        self.repo = user_repo
    
    async def create_user(self, db, user_in):
        # 业务逻辑
        return await self.repo.create(db, obj_in=user_in)

user_service = UserService()
```

5. **创建API** (`api/user.py`)
```python
@router.post("/")
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_async_db)):
    return await user_service.create_user(db, user_in)
```

6. **注册路由** (`app/main.py`)
```python
from backend.api import user
app.include_router(user.router, prefix="/user", tags=["用户模块"])
```

## 迁移指南

如果你有自定义代码需要迁移：

1. **Model层**：无需修改，只需更新import路径
2. **Repository层**：将 `crud` 目录下的文件复制到 `repositories`，更新import路径
3. **Service层**：从API层提取业务逻辑到新的Service文件
4. **API层**：更新为调用Service层而非直接调用Repository层

## 注意事项

1. **不要跨层调用**：
   - ❌ API层不能直接调用Repository层
   - ❌ Repository层不能调用Service层
   - ✅ API → Service → Repository

2. **依赖注入**：所有层都使用依赖注入方式传递数据库会话

3. **异常处理**：
   - Repository层抛出技术异常
   - Service层捕获技术异常，抛出业务异常
   - API层捕获业务异常，转换为HTTP错误响应

4. **事务管理**：事务应该在Service层或API层控制，Repository层不负责事务
