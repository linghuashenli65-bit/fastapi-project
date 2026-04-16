# 统一日志和异常处理使用指南

本文档介绍如何使用项目的统一日志、响应和异常处理模块。

## 目录

1. [日志模块使用](#日志模块使用)
2. [响应模块使用](#响应模块使用)
3. [异常处理使用](#异常处理使用)
4. [完整示例](#完整示例)

## 日志模块使用

### 基础使用

```python
from backend.core.logger import get_logger, setup_logger

# 获取 logger 实例
logger = get_logger("my_module")

# 记录不同级别的日志
logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

### 使用结构化日志

```python
from backend.core.logger import get_logger

logger = get_logger("my_module")

# 使用结构化日志，可以传入额外的上下文信息
logger.info(
    "用户登录",
    user_id=123,
    username="zhangsan",
    ip="192.168.1.1"
)
```

### 使用专用日志记录器

```python
from backend.core.logger import api_logger, db_logger, ai_logger

# API 日志记录器
await api_logger.log_request(
    method="POST",
    path="/api/v1/student/",
    client_ip="192.168.1.1",
    query_params="name=张三"
)

await api_logger.log_response(
    method="POST",
    path="/api/v1/student/",
    status_code=200,
    duration=0.123
)

await api_logger.log_error(
    method="POST",
    path="/api/v1/student/",
    error=Exception("参数错误")
)

# 数据库日志记录器
db_logger.log_query(
    query="SELECT * FROM student WHERE id = ?",
    params={"id": 123},
    duration=0.045
)

db_logger.log_slow_query(
    query="SELECT * FROM student WHERE name LIKE ?",
    duration=1.5,
    threshold=1.0
)

db_logger.log_error(
    error=Exception("连接超时"),
    query="SELECT * FROM student"
)

# AI 日志记录器
ai_logger.log_request(
    model="qwen",
    prompt="查询所有学生",
    endpoint="https://dashscope.aliyuncs.com/..."
)

ai_logger.log_response(
    model="qwen",
    response_length=1000,
    duration=2.345
)

ai_logger.log_error(
    model="qwen",
    error=Exception("API 调用失败")
)
```

### 自定义日志配置

```python
from backend.core.logger import setup_logger
from pathlib import Path

# 自定义日志配置
custom_logger = setup_logger(
    log_level="DEBUG",
    log_dir=Path("custom_logs"),
    app_name="my_app"
)
```

## 响应模块使用

### 使用响应构建器

```python
from backend.core.response import (
    ResponseBuilder,
    success,
    error,
    pagination,
    created,
    updated,
    deleted,
    not_found
)

# 方法1：使用 ResponseBuilder
response = ResponseBuilder.success(
    data={"id": 1, "name": "张三"},
    msg="查询成功"
)
# 返回: {"code": 200, "msg": "查询成功", "data": {"id": 1, "name": "张三"}}

# 方法2：使用快捷函数
response = success({"id": 1, "name": "张三"}, "查询成功")
response = error("参数错误", 400)
response = pagination(data, count=100, page=1, page_size=10)
response = created({"id": 1, "name": "张三"}, "创建成功")
response = updated({"id": 1, "name": "李四"}, "更新成功")
response = deleted("删除成功")
response = not_found("学生不存在")
```

### 在 API 中使用

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.response import success, error, pagination
from backend.services.student_service import student_service

router = APIRouter()

@router.get("/")
async def get_students(
    page: int = 1,
    size: int = 10,
    name: str = None,
    db: AsyncSession = Depends(get_async_db)
):
    """获取学生列表"""
    try:
        # 调用 service 层
        data = await student_service.get_students(db, page, size, name)
        
        # 返回分页响应
        return pagination(
            data=data["students"],
            count=data["count"],
            page=page,
            page_size=size
        )
    except Exception as e:
        return error(f"获取学生列表失败: {str(e)}", 500)

@router.post("/")
async def create_student(
    student_in: StudentCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """创建学生"""
    try:
        student = await student_service.create_student(db, student_in)
        return success(student, "创建成功")
    except ValueError as e:
        return error(str(e), 400)
```

### 使用响应模型

```python
from backend.core.response import SuccessResponse, ErrorResponse, PaginationResponse

# 定义返回类型
@router.get("/", response_model=PaginationResponse)
async def get_students():
    """获取学生列表"""
    # ... 业务逻辑
    return PaginationResponse.create(
        data=students,
        count=total_count,
        page=page,
        page_size=size
    )

# 自定义响应
@router.post("/", response_model=SuccessResponse[StudentInDB])
async def create_student():
    """创建学生"""
    # ... 业务逻辑
    return SuccessResponse(data=student, msg="创建成功")
```

## 异常处理使用

### 抛出自定义异常

```python
from backend.core.exceptions import (
    NotFoundException,
    ConflictException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    DatabaseException,
    AIException,
    DuplicateException,
    InvalidParameterException,
)

# 资源不存在
raise NotFoundException("学生不存在")
raise NotFoundException(resource="学生")

# 资源冲突
raise ConflictException("学号已存在")

# 验证失败
raise ValidationException("参数验证失败", errors=["姓名不能为空", "学号格式错误"])

# 认证/授权失败
raise AuthenticationException("Token 已过期")
raise AuthorizationException("无权限访问")

# 数据库错误
raise DatabaseException("数据库连接失败", original_error=e)

# AI 服务错误
raise AIException("AI 服务调用失败", model="qwen")

# 数据重复
raise DuplicateException(field="学号")

# 参数错误
raise InvalidParameterException("年龄必须大于0")
```

### 使用快捷函数

```python
from backend.core.exceptions import (
    raise_not_found,
    raise_conflict,
    raise_validation_error,
    raise_unauthorized,
    raise_forbidden,
    raise_database_error,
    raise_ai_error,
    raise_duplicate,
    raise_invalid_parameter,
)

# 资源不存在
raise_not_found("学生不存在")
raise_not_found(resource="学生")

# 资源冲突
raise_conflict("学号已存在")

# 验证失败
raise_validation_error(errors=["姓名不能为空"])

# 认证/授权失败
raise_unauthorized("Token 已过期")
raise_forbidden("无权限访问")

# 数据库错误
raise_database_error(e, "数据库连接失败")

# AI 服务错误
raise_ai_error("AI 服务调用失败", model="qwen")

# 数据重复
raise_duplicate(field="学号")

# 参数错误
raise_invalid_parameter("年龄必须大于0")
```

### 使用异常处理装饰器

```python
from backend.core.exceptions import handle_exceptions, async_exception_handler

# 方法1：通用异常处理装饰器
@handle_exceptions(default_msg="操作失败", default_code=500, log_error=True)
async def some_function():
    # 可能抛出异常的代码
    pass

# 方法2：捕获特定异常
@async_exception_handler(ValueError, default_msg="参数错误", default_code=400)
async def validate_data(data):
    if not data:
        raise ValueError("数据不能为空")
    return data

# 方法3：捕获多个异常
@async_exception_handler((ValueError, TypeError), default_msg="数据格式错误")
async def process_data(data):
    # 处理数据
    pass
```

### 在 API 中使用

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.exceptions import (
    NotFoundException,
    ConflictException,
    raise_not_found,
    raise_duplicate,
)
from backend.services.student_service import student_service

router = APIRouter()

@router.get("/{student_id}")
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """获取学生详情"""
    student = await student_service.get_student(db, student_id)
    
    # 检查学生是否存在
    if not student:
        raise NotFoundException("学生不存在")
    
    return student

@router.post("/")
async def create_student(
    student_in: StudentCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """创建学生"""
    try:
        # 检查学号是否已存在
        existing = await student_service.get_by_student_no(db, student_in.student_no)
        if existing:
            raise ConflictException("学号已存在")
        
        student = await student_service.create_student(db, student_in)
        return student
    except ConflictException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 使用快捷函数
@router.put("/{student_id}")
async def update_student(
    student_id: int,
    student_in: StudentUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """更新学生"""
    student = await student_service.get_student(db, student_id)
    if not student:
        raise_not_found("学生")
    
    # 检查学号是否与其他学生冲突
    if student_in.student_no and student_in.student_no != student.student_no:
        existing = await student_service.get_by_student_no(db, student_in.student_no)
        if existing:
            raise_duplicate(field="学号")
    
    return await student_service.update_student(db, student, student_in)
```

### 自定义异常

```python
from backend.core.exceptions import BaseAPIException

class StudentNotFoundException(BaseAPIException):
    """学生不存在异常"""
    def __init__(self, student_id: int = None):
        msg = f"学生不存在"
        if student_id:
            msg = f"学生(ID: {student_id})不存在"
        super().__init__(msg, 404)

# 使用
@router.get("/{student_id}")
async def get_student(student_id: int):
    student = await get_student_by_id(student_id)
    if not student:
        raise StudentNotFoundException(student_id)
    return student
```

## 完整示例

### 在 Service 层使用

```python
from backend.core.logger import get_logger
from backend.core.exceptions import NotFoundException, ConflictException
from backend.repositories.student_repo import student_repo

logger = get_logger("student_service")

class StudentService:
    def __init__(self):
        self.repo = student_repo
    
    async def get_student(self, db, student_id: int):
        """获取学生详情"""
        logger.info(f"查询学生详情", student_id=student_id)
        
        student = await self.repo.get(db, student_id)
        if not student:
            logger.warning(f"学生不存在", student_id=student_id)
            raise NotFoundException("学生不存在")
        
        logger.info(f"查询成功", student_id=student_id, student_name=student.name)
        return student
    
    async def create_student(self, db, student_in):
        """创建学生"""
        logger.info(f"创建学生", student_no=student_in.student_no, name=student_in.name)
        
        # 检查学号是否已存在
        existing = await self.repo.get_by_student_no(db, student_in.student_no)
        if existing:
            logger.warning(f"学号已存在", student_no=student_in.student_no)
            raise ConflictException("学号已存在")
        
        # 创建学生
        student = await self.repo.create(db, obj_in=student_in)
        logger.info(f"创建成功", student_id=student.id, student_no=student.student_no)
        
        return student

student_service = StudentService()
```

### 在 API 层使用

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.response import success, error, created, not_found
from backend.core.logger import api_logger
from backend.services.student_service import student_service
from backend.core.database import get_async_db

router = APIRouter()

@router.get("/")
async def get_students(
    page: int = 1,
    size: int = 10,
    name: str = None,
    db: AsyncSession = Depends(get_async_db)
):
    """获取学生列表"""
    try:
        data = await student_service.get_students(db, page, size, name)
        return success(data["data"], "查询成功")
    except Exception as e:
        await api_logger.log_error("GET", "/student/", e)
        return error(f"获取学生列表失败: {str(e)}", 500)

@router.post("/")
async def create_student(
    student_in: StudentCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """创建学生"""
    try:
        student = await student_service.create_student(db, student_in)
        return created(student, "创建成功")
    except NotFoundException as e:
        return error(str(e), 404)
    except ConflictException as e:
        return error(str(e), 409)
    except Exception as e:
        await api_logger.log_error("POST", "/student/", e)
        return error(f"创建学生失败: {str(e)}", 500)

@router.get("/{student_id}")
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """获取学生详情"""
    try:
        student = await student_service.get_student(db, student_id)
        return success(student, "查询成功")
    except NotFoundException as e:
        return not_found(str(e))
    except Exception as e:
        await api_logger.log_error("GET", f"/student/{student_id}", e)
        return error(f"获取学生详情失败: {str(e)}", 500)
```

## 最佳实践

### 1. 日志记录

- ✅ 使用结构化日志，添加上下文信息
- ✅ 合理选择日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
- ✅ 在关键操作处记录日志
- ✅ 记录异常的详细信息
- ❌ 不要在生产环境中记录敏感信息
- ❌ 不要在循环中频繁记录日志

### 2. 响应格式

- ✅ 统一使用响应构建器或响应模型
- ✅ 使用合适的 HTTP 状态码
- ✅ 提供清晰的错误消息
- ✅ 返回数据时进行验证和过滤
- ❌ 不要返回敏感信息
- ❌ 不要在前端暴露技术细节

### 3. 异常处理

- ✅ 使用自定义异常类
- ✅ 在适当的地方抛出异常
- ✅ 使用异常处理装饰器简化代码
- ✅ 记录异常的详细信息
- ❌ 不要捕获所有异常却不处理
- ❌ 不要在异常中暴露敏感信息

### 4. 分层架构

- ✅ 在 Service 层处理业务逻辑和异常
- ✅ 在 API 层进行请求验证和响应格式化
- ✅ 使用中间件记录请求和响应
- ❌ 不要在 API 层直接操作数据库
- ❌ 不要跨层调用（如 API 直接调用 Repository）

## 故障排查

### 日志文件位置

默认日志文件位置：
- 普通日志：`logs/student_management_YYYYMMDD.log`
- 错误日志：`logs/student_management_error_YYYYMMDD.log`

### 查看日志

```bash
# 查看最新日志
tail -f logs/student_management_$(date +%Y%m%d).log

# 查看错误日志
tail -f logs/student_management_error_$(date +%Y%m%d).log

# 搜索特定错误
grep "ERROR" logs/student_management_$(date +%Y%m%d).log
```

### 常见问题

**问题1：日志文件没有生成**
- 检查日志目录是否有写权限
- 检查日志配置是否正确

**问题2：异常没有被捕获**
- 检查异常处理器是否正确注册
- 检查是否使用了正确的异常类

**问题3：响应格式不一致**
- 确保所有 API 都使用了统一的响应构建器
- 检查是否有直接返回非标准格式的情况

## 相关文档

- [后端文档](./README.md)
- [API 文档](http://localhost:8888/docs)
- [迁移指南](./MIGRATION_GUIDE.md)
- [重构说明](./REFACTORING.md)
