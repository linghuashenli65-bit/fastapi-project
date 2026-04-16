# 学生管理系统 - 后端文档

基于 FastAPI 的学生管理系统后端，采用 MVC 分层架构。

## 目录结构

```
backend/
├── app/                   # 应用入口
│   └── main.py           # FastAPI 主应用
├── api/                   # API 路由层 (Controller)
│   ├── agent.py          # AI 模块 API
│   ├── class_student.py  # 班级模块 API
│   ├── employment.py     # 就业模块 API
│   ├── score.py          # 成绩模块 API
│   ├── student.py        # 学生模块 API
│   └── teacher.py        # 教师模块 API
├── core/                 # 核心配置
│   ├── config.py         # 配置文件（数据库、API 密钥等）
│   └── database.py       # 数据库会话管理
├── models/               # 数据模型层 (Model)
│   ├── agent.py         # AI 相关模型（SQL 生成、分析）
│   ├── class_.py        # 班级模型
│   ├── dashboard.py      # 仪表板模型
│   ├── employment.py     # 就业模型
│   ├── llm.py           # LLM 接口（Qwen、DeepSeek）
│   ├── score.py         # 成绩模型
│   ├── student.py       # 学生模型
│   ├── student_class.py  # 学生-班级关联模型
│   └── teacher.py       # 教师模型
├── repositories/         # 数据访问层 (Repository)
│   ├── base.py          # 基础 CRUD 类
│   ├── class_repo.py    # 班级数据访问
│   ├── employment_repo.py # 就业数据访问
│   ├── score_repo.py    # 成绩数据访问
│   ├── sql_service.py   # SQL 执行服务
│   ├── student_repo.py  # 学生数据访问
│   └── teacher_repo.py  # 教师数据访问
├── schemas/             # 数据传输对象 (Schema/DTO)
│   ├── agent.py         # AI 相关 Schema
│   ├── Class.py         # 班级 Schema
│   ├── employment.py    # 就业 Schema
│   ├── score.py        # 成绩 Schema
│   ├── student.py      # 学生 Schema
│   └── teacher.py      # 教师 Schema
├── services/            # 业务逻辑层 (Service)
│   ├── class_service.py   # 班级业务逻辑
│   ├── employment_service.py # 就业业务逻辑
│   ├── student_service.py # 学生业务逻辑
│   └── teacher_service.py # 教师业务逻辑
├── utils/               # 工具函数
│   └── helpers.py      # 辅助函数（如响应清洗）
├── static/             # 静态文件 (View)
│   ├── index.html      # 主页面
│   ├── style.css       # 样式文件
│   ├── test.html       # 测试页面
│   └── js/            # JavaScript 文件
│       ├── api.js      # API 调用封装
│       ├── config.js   # 配置
│       ├── utils.js    # 工具函数
│       └── modules/    # 功能模块
│           ├── ai.js
│           ├── class.js
│           ├── employment.js
│           ├── score.js
│           ├── student.js
│           └── teacher.js
├── MIGRATION_GUIDE.md  # 迁移指南
└── REFACTORING.md      # 重构说明
```

## 技术栈

### 核心框架
- **FastAPI**：现代、快速的 Web 框架
- **SQLAlchemy**：Python SQL 工具包和 ORM
- **Pydantic**：数据验证和设置管理
- **AsyncMy**：MySQL 异步驱动

### AI 集成
- **通义千问 (Qwen)**：阿里云大语言模型 API
- **DeepSeek**：DeepSeek 大语言模型 API
- **HTTPX**：异步 HTTP 客户端

### 数据库
- **MySQL 5.7+**：关系型数据库

## 架构设计

### MVC 分层架构

```
┌─────────────────────────────────────────┐
│         API Layer (api/)              │
│  - HTTP 请求处理                      │
│  - 参数验证                           │
│  - 响应格式化                         │
└──────────────┬────────────────────────┘
               │ 调用
┌──────────────▼────────────────────────┐
│      Service Layer (services/)         │
│  - 业务逻辑处理                       │
│  - 数据验证和转换                     │
│  - 事务管理                           │
└──────────────┬────────────────────────┘
               │ 调用
┌──────────────▼────────────────────────┐
│   Repository Layer (repositories/)    │
│  - 数据库 CRUD 操作                   │
│  - 复杂查询                          │
│  - 数据持久化                         │
└──────────────┬────────────────────────┘
               │ 映射
┌──────────────▼────────────────────────┐
│      Model Layer (models/)            │
│  - 数据库表结构定义                   │
│  - ORM 模型                          │
└───────────────────────────────────────┘
```

### 层次职责

#### API 层 (`api/`)
- **职责**：处理 HTTP 请求和响应
- **内容**：
  - 定义路由 (Router)
  - 请求参数验证
  - 调用 Service 层
  - 格式化响应数据
  - 异常处理

**示例**：
```python
@router.post("/", response_model=StudentInDB)
async def create_student(
    student_in: StudentCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """创建新学生"""
    return await student_service.create_student(db, student_in)
```

#### Service 层 (`services/`)
- **职责**：业务逻辑处理
- **内容**：
  - 调用 Repository 层
  - 业务规则实现
  - 数据转换和验证
  - 事务管理

**示例**：
```python
class StudentService:
    async def create_student(self, db: AsyncSession, student_in: StudentCreate):
        # 业务逻辑：检查学号是否重复
        existing = await self.repo.get_by_student_no(db, student_in.student_no)
        if existing:
            raise ValueError("学号已存在")
        return await self.repo.create(db, obj_in=student_in)
```

#### Repository 层 (`repositories/`)
- **职责**：数据访问
- **内容**：
  - 继承 BaseCRUD 获得通用 CRUD 方法
  - 实现特定查询方法
  - 封装数据库操作
  - 不包含业务逻辑

**示例**：
```python
class StudentRepo(BaseCRUD[Student, StudentCreate, StudentUpdate]):
    def __init__(self):
        super().__init__(Student)

    async def get_by_student_no(self, db: AsyncSession, student_no: str):
        stmt = select(Student).where(Student.student_no == student_no)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
```

#### Model 层 (`models/`)
- **职责**：数据库表结构定义
- **内容**：
  - 表结构定义
  - 字段类型和约束
  - 表关系（外键）
  - 索引定义

**示例**：
```python
class Student(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True)
    student_no = Column(String(50), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    # ... 其他字段
```

#### Schema 层 (`schemas/`)
- **职责**：数据传输对象（DTO）
- **内容**：
  - 请求模型（Create/Update）
  - 响应模型（Response/Out）
  - 数据验证规则

**示例**：
```python
class StudentCreate(BaseModel):
    student_no: str
    name: str
    gender: str
    # ... 其他字段

class StudentInDB(BaseModel):
    id: int
    student_no: str
    name: str
    # ... 其他字段
    class Config:
        from_attributes = True
```

## 数据库设计

### 表结构

#### 1. sequence (序号生成表)
```sql
CREATE TABLE sequence (
    seq_name VARCHAR(50) PRIMARY KEY,
    current_val INT DEFAULT 0
);
```

#### 2. class (班级表)
```sql
CREATE TABLE class (
    id INT PRIMARY KEY AUTO_INCREMENT,
    class_no VARCHAR(50) UNIQUE,
    class_name VARCHAR(100),
    start_date DATE,
    deleted_at DATETIME DEFAULT '1900-01-01 00:00:00',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 3. teacher (教师表)
```sql
CREATE TABLE teacher (
    id INT PRIMARY KEY AUTO_INCREMENT,
    teacher_no VARCHAR(50) UNIQUE,
    name VARCHAR(50),
    gender CHAR(1),
    phone VARCHAR(20),
    title VARCHAR(50),
    deleted_at DATETIME DEFAULT '1900-01-01 00:00:00',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 4. teacher_class (教师带班表)
```sql
CREATE TABLE teacher_class (
    id INT PRIMARY KEY AUTO_INCREMENT,
    teacher_no VARCHAR(50),
    class_no VARCHAR(50),
    role ENUM('head_teacher', 'course_teacher', 'assistant'),
    start_date DATE,
    end_date DATE,
    is_current TINYINT DEFAULT 0,
    deleted_at DATETIME DEFAULT '1900-01-01 00:00:00',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_no) REFERENCES teacher(teacher_no),
    FOREIGN KEY (class_no) REFERENCES class(class_no)
);
```

#### 5. student (学生表)
```sql
CREATE TABLE student (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_no VARCHAR(50) UNIQUE,
    name VARCHAR(50),
    gender CHAR(1),
    birth_date DATE,
    birthplace VARCHAR(100),
    graduated_school VARCHAR(100),
    major VARCHAR(100),
    enrollment_date DATE,
    graduation_date DATE,
    education TINYINT,
    consultant_no VARCHAR(50),
    deleted_at DATETIME DEFAULT '1900-01-01 00:00:00',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (consultant_no) REFERENCES teacher(teacher_no)
);
```

#### 6. student_class (学生班级关联表)
```sql
CREATE TABLE student_class (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_no VARCHAR(50),
    class_no VARCHAR(50),
    start_date DATE,
    end_date DATE,
    is_current TINYINT DEFAULT 0,
    reason VARCHAR(50),
    deleted_at DATETIME DEFAULT '1900-01-01 00:00:00',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_no) REFERENCES student(student_no),
    FOREIGN KEY (class_no) REFERENCES class(class_no)
);
```

#### 7. score (成绩表)
```sql
CREATE TABLE score (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_no VARCHAR(50),
    class_no VARCHAR(50),
    start_date DATE,
    exam_sequence INT,
    exam_date DATE,
    score DECIMAL(5,2),
    deleted_at DATETIME DEFAULT '1900-01-01 00:00:00',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_no) REFERENCES student(student_no),
    FOREIGN KEY (class_no) REFERENCES class(class_no)
);
```

#### 8. employment (就业表)
```sql
CREATE TABLE employment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_no VARCHAR(50),
    company_name VARCHAR(100),
    job_title VARCHAR(100),
    salary INT,
    offer_date DATE,
    employment_start_date DATE,
    record_type ENUM('offer', 'employment'),
    is_current TINYINT DEFAULT 0,
    deleted_at DATETIME DEFAULT '1900-01-01 00:00:00',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_no) REFERENCES student(student_no)
);
```

### 软删除策略

所有表都使用 `deleted_at` 字段实现软删除：
- `deleted_at = '1900-01-01 00:00:00'` 表示未删除
- `deleted_at > '1900-01-01 00:00:00'` 表示已删除

查询时需要过滤已删除记录：
```sql
WHERE deleted_at = '1900-01-01 00:00:00'
```

## AI 功能实现

### AI 模块架构

```
API Layer (api/agent.py)
    ↓
Dashboard Generation (models/dashboard.py)
    ↓
├─ Task Decomposition (split_tasks)
├─ SQL Generation (generate_sql)
├─ SQL Execution (execute_sql)
├─ Chart Type Selection (ai_choose_chart_type)
└─ Analysis Generation (generate_analysis)
```

### LLM 接口

#### 通义千问 (Qwen)
- **URL**: `https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation`
- **请求格式**：
```json
{
  "model": "qwen-max",
  "input": {
    "messages": [
      {"role": "user", "content": "your prompt"}
    ]
  },
  "parameters": {
    "temperature": 0.7
  }
}
```
- **响应格式**：
```json
{
  "output": {
    "text": "AI response"
  },
  "usage": {...}
}
```

#### DeepSeek
- **URL**: `https://api.deepseek.com/v1/chat/completions`
- **请求格式**：
```json
{
  "model": "deepseek-chat",
  "messages": [
    {"role": "user", "content": "your prompt"}
  ],
  "temperature": 0.7
}
```
- **响应格式**：
```json
{
  "choices": [
    {
      "message": {
        "content": "AI response"
      }
    }
  ]
}
```

### AI 功能使用

#### 1. 自然语言 SQL 查询
```python
from backend.models.agent import agent_sql

result = await agent_sql(
    query="查询所有不及格的学生",
    model="qwen"
)
# 返回: {"code": 200, "msg": "success", "sql": "...", "data": [...]}
```

#### 2. 智能数据分析（流式）
```python
from backend.models.dashboard import build_dashboard

async for event in build_dashboard(
    query="分析各班级的就业情况",
    model="qwen",
    analysis_length="medium"
):
    # 事件类型：split, sql_generate, sql_execute, chart_type,
    #        build_chart, postprocess, analysis, complete
    print(event)
```

## 开发指南

### 添加新功能

#### 步骤 1：定义 Model
```python
# models/user.py
from sqlalchemy import Column, Integer, String
from backend.core.database import Base

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
```

#### 步骤 2：定义 Schema
```python
# schemas/user.py
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str

class UserUpdate(BaseModel):
    name: str = None
    email: str = None

class UserInDB(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True
```

#### 步骤 3：创建 Repository
```python
# repositories/user_repo.py
from backend.repositories.base import BaseCRUD
from backend.models.user import User
from backend.schemas.user import UserCreate, UserUpdate

class UserRepo(BaseCRUD[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str):
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

user_repo = UserRepo()
```

#### 步骤 4：创建 Service
```python
# services/user_service.py
class UserService:
    def __init__(self):
        self.repo = user_repo

    async def create_user(self, db: AsyncSession, user_in: UserCreate):
        # 检查邮箱是否已存在
        existing = await self.repo.get_by_email(db, user_in.email)
        if existing:
            raise ValueError("邮箱已被注册")
        return await self.repo.create(db, obj_in=user_in)

    async def get_user_by_email(self, db: AsyncSession, email: str):
        return await self.repo.get_by_email(db, email)

user_service = UserService()
```

#### 步骤 5：创建 API
```python
# api/user.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_async_db
from backend.services.user_service import user_service
from backend.schemas.user import UserCreate, UserInDB

router = APIRouter()

@router.post("/", response_model=UserInDB, summary="创建用户")
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """创建新用户"""
    try:
        return await user_service.create_user(db, user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/email/{email}", response_model=UserInDB, summary="按邮箱查询用户")
async def get_user_by_email(
    email: str,
    db: AsyncSession = Depends(get_async_db)
):
    """按邮箱查询用户"""
    user = await user_service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
```

#### 步骤 6：注册路由
```python
# app/main.py
from backend.api import user

app.include_router(
    user.router,
    prefix="/user",
    tags=["用户模块"]
)
```

### 测试

#### 运行测试
```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 运行测试
pytest tests/
```

#### 测试示例
```python
# tests/test_student.py
import pytest
from httpx import AsyncClient
from backend.app.main import app

@pytest.mark.asyncio
async def test_create_student():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/student/",
            json={
                "student_no": "250000001",
                "name": "张三",
                "gender": "M"
            }
        )
        assert response.status_code == 200
        assert response.json()["name"] == "张三"
```

## 配置说明

### 环境变量

创建 `.env` 文件：

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=student_management_system

# AI API 配置（可选，也可以在 config.py 中直接配置）
QWEN_API_KEY=your_qwen_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### 配置文件

`core/config.py` 包含所有配置项：

```python
# API 配置
API_CONFIG = {
    "qwen": {
        "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
        "api_key": "your-qwen-api-key",
        "model": "qwen-max"
    },
    "deepseek": {
        "url": "https://api.deepseek.com/v1/chat/completions",
        "api_key": "your-deepseek-api-key",
        "model": "deepseek-chat"
    }
}

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "student_management_system"
}
```

## 常见问题

### 1. 数据库连接失败
**问题**：`pymysql.err.OperationalError`
**解决**：
- 检查 MySQL 服务是否启动
- 检查数据库配置是否正确
- 确保数据库已创建

### 2. AI API 调用失败
**问题**：`调用Qwen API失败: 'choices'`
**解决**：
- 检查 API 密钥是否正确
- 检查网络连接
- 查看详细的错误日志

### 3. SQL 查询错误
**问题**：`Unknown column 'xxx' in 'where clause'`
**解决**：
- 检查 AI 生成的 SQL 是否使用正确的字段名
- 确保 `deleted_at` 字段而不是 `is_deleted`

### 4. 导入错误
**问题**：`ModuleNotFoundError: No module named 'backend.xxx'`
**解决**：
- 确保从项目根目录运行
- 检查 Python 路径配置

## 性能优化

### 数据库优化
1. 添加适当的索引
2. 使用连接池
3. 优化复杂查询
4. 使用分页查询

### 代码优化
1. 使用异步操作
2. 缓存常用数据
3. 减少数据库查询次数
4. 使用批量操作

## 部署

### 生产环境配置

1. **使用 Gunicorn**
```bash
gunicorn backend.app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

2. **使用 Docker**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["gunicorn", "backend.app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

3. **使用 Nginx 反向代理**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /app/backend/static/;
    }
}
```

## 相关文档

- [项目迁移指南](./MIGRATION_GUIDE.md)
- [MVC 重构说明](./REFACTORING.md)
- [项目 README](../README.md)

## 支持

如有问题，请提交 Issue 或联系项目维护者。
