# 统一日志和异常处理功能说明

## 概述

本次更新为项目添加了完整的日志记录、响应格式化和异常处理系统，大大提升了项目的可维护性、可观测性和开发效率。

## 新增文件

### 1. 核心模块 (`backend/core/`)

#### `logger.py` - 统一日志模块
- **功能**：基于 Loguru 的高性能日志系统
- **特性**：
  - ✅ 结构化日志记录
  - ✅ 多级别日志（DEBUG/INFO/WARNING/ERROR/CRITICAL）
  - ✅ 彩色控制台输出
  - ✅ 自动文件轮转（10MB）
  - ✅ 自动清理（30天）
  - ✅ 分级别日志文件（普通日志 + 错误日志）
  - ✅ 专用日志记录器（API、数据库、AI）

- **主要类和函数**：
  - `setup_logger()` - 配置日志系统
  - `get_logger()` - 获取 logger 实例
  - `APILogger` - API 日志记录器
  - `DBLogger` - 数据库日志记录器
  - `AILogger` - AI 日志记录器

#### `response.py` - 统一响应模块
- **功能**：标准化的 API 响应格式
- **特性**：
  - ✅ 统一的响应格式（code/msg/data）
  - ✅ 多种响应类型（成功、错误、分页、批量操作等）
  - ✅ 响应构建器模式
  - ✅ 泛型响应模型
  - ✅ 快捷响应函数

- **主要类和函数**：
  - `ResponseModel` - 基础响应模型
  - `SuccessResponse` - 成功响应
  - `ErrorResponse` - 错误响应
  - `PaginationResponse` - 分页响应
  - `ResponseBuilder` - 响应构建器
  - `success()`, `error()`, `pagination()` - 快捷函数

#### `exceptions.py` - 统一异常处理模块
- **功能**：自定义异常类和异常处理器
- **特性**：
  - ✅ 自定义异常类体系
  - ✅ 统一的异常处理器
  - ✅ 异常处理装饰器
  - ✅ 快捷异常抛出函数
  - ✅ 详细的异常日志记录

- **主要类和函数**：
  - `BaseAPIException` - 基础 API 异常
  - `NotFoundException` - 资源不存在异常
  - `ConflictException` - 资源冲突异常
  - `ValidationException` - 数据验证异常
  - `AuthenticationException` - 认证异常
  - `AuthorizationException` - 授权异常
  - `DatabaseException` - 数据库异常
  - `AIException` - AI 服务异常
  - `raise_not_found()`, `raise_conflict()` - 快捷函数

### 2. 中间件 (`backend/middlewares/`)

#### `logging_middleware.py` - 日志中间件
- **功能**：自动记录请求和响应
- **特性**：
  - ✅ 自动记录所有请求和响应
  - ✅ 性能监控（响应时间）
  - ✅ 客户端 IP 记录（支持代理）
  - ✅ 请求 ID 生成
  - ✅ 错误日志记录

- **主要类**：
  - `LoggingMiddleware` - 主要日志中间件
  - `ErrorLoggingMiddleware` - 错误日志中间件
  - `RequestLoggingMiddleware` - 简化版请求日志中间件

### 3. 应用更新 (`backend/app/`)

#### `main.py` - 主应用文件
- **更新内容**：
  - ✅ 集成日志系统
  - ✅ 注册异常处理器
  - ✅ 注册日志中间件
  - ✅ 添加健康检查端点
  - ✅ 添加根路径路由

### 4. 文档 (`backend/`)

#### `USAGE_GUIDE.md` - 使用指南
- **内容**：
  - 日志模块使用说明
  - 响应模块使用说明
  - 异常处理使用说明
  - 完整示例代码
  - 最佳实践
  - 故障排查指南

## 核心功能

### 1. 日志记录

#### 基础使用
```python
from backend.core.logger import get_logger

logger = get_logger("my_module")
logger.info("用户登录", user_id=123, username="zhangsan")
```

#### 专用日志记录器
```python
from backend.core.logger import api_logger, db_logger, ai_logger

# API 日志
await api_logger.log_request(method="POST", path="/api/v1/student/", client_ip="192.168.1.1")
await api_logger.log_response(method="POST", path="/api/v1/student/", status_code=200, duration=0.123)

# 数据库日志
db_logger.log_query(query="SELECT * FROM student", duration=0.045)

# AI 日志
ai_logger.log_request(model="qwen", prompt="查询学生", endpoint="...")
ai_logger.log_response(model="qwen", response_length=1000, duration=2.345)
```

### 2. 响应格式化

#### 使用响应构建器
```python
from backend.core.response import success, error, pagination

# 成功响应
return success(data={"id": 1, "name": "张三"}, msg="查询成功")

# 错误响应
return error(msg="参数错误", code=400)

# 分页响应
return pagination(data=students, count=100, page=1, page_size=10)
```

### 3. 异常处理

#### 抛出异常
```python
from backend.core.exceptions import NotFoundException, ConflictException

# 资源不存在
raise NotFoundException("学生不存在")

# 资源冲突
raise ConflictException("学号已存在")
```

#### 使用异常处理装饰器
```python
from backend.core.exceptions import handle_exceptions

@handle_exceptions(default_msg="操作失败", default_code=500)
async def some_function():
    # 可能抛出异常的代码
    pass
```

## 日志文件

### 文件位置
- 普通日志：`logs/student_management_YYYYMMDD.log`
- 错误日志：`logs/student_management_error_YYYYMMDD.log`

### 日志级别
- DEBUG：详细的调试信息
- INFO：一般信息
- WARNING：警告信息
- ERROR：错误信息
- CRITICAL：严重错误

### 日志格式
```
2026-04-16 17:30:00.123 | INFO     | api:log_request:45 - Request: POST /api/v1/student/ from 192.168.1.1
```

## 响应格式

### 成功响应
```json
{
  "code": 200,
  "msg": "success",
  "data": {...}
}
```

### 错误响应
```json
{
  "code": 400,
  "msg": "参数错误",
  "data": null
}
```

### 分页响应
```json
{
  "code": 200,
  "msg": "success",
  "data": [...],
  "count": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10
}
```

## 异常处理

### 异常处理器
- `base_api_exception_handler` - 基础 API 异常
- `http_exception_handler` - HTTP 异常
- `validation_exception_handler` - 验证异常
- `general_exception_handler` - 通用异常

### 自定义异常
- `BaseAPIException` - 基础 API 异常
- `NotFoundException` - 资源不存在（404）
- `ConflictException` - 资源冲突（409）
- `ValidationException` - 数据验证失败（400）
- `AuthenticationException` - 认证失败（401）
- `AuthorizationException` - 授权失败（403）
- `DatabaseException` - 数据库异常（500）
- `AIException` - AI 服务异常（500）

## 最佳实践

### 1. 日志记录
- ✅ 使用结构化日志，添加上下文信息
- ✅ 合理选择日志级别
- ✅ 在关键操作处记录日志
- ✅ 记录异常的详细信息
- ❌ 不要记录敏感信息

### 2. 响应格式
- ✅ 统一使用响应构建器
- ✅ 使用合适的 HTTP 状态码
- ✅ 提供清晰的错误消息
- ❌ 不要返回敏感信息

### 3. 异常处理
- ✅ 使用自定义异常类
- ✅ 在适当的地方抛出异常
- ✅ 使用异常处理装饰器
- ✅ 记录异常的详细信息
- ❌ 不要捕获所有异常却不处理

## 使用示例

### 完整的 API 示例
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.response import success, error, not_found
from backend.core.exceptions import NotFoundException, ConflictException
from backend.core.logger import api_logger
from backend.services.student_service import student_service

router = APIRouter()

@router.get("/")
async def get_students(
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_async_db)
):
    """获取学生列表"""
    try:
        data = await student_service.get_students(db, page, size)
        return success(data, "查询成功")
    except Exception as e:
        await api_logger.log_error("GET", "/student/", e)
        return error(f"获取学生列表失败: {str(e)}", 500)

@router.get("/{student_id}")
async def get_student(student_id: int, db: AsyncSession = Depends(get_async_db)):
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

## 更新内容

### 依赖更新
- 添加 `loguru==0.7.2` 到 `requirements.txt`

### 应用更新
- 更新 `backend/app/main.py`：
  - 集成日志系统
  - 注册异常处理器
  - 注册日志中间件
  - 添加健康检查端点

### 文档更新
- 创建 `backend/USAGE_GUIDE.md` 使用指南
- 更新 `CHANGELOG.md` 更新日志

## 优势

### 1. 可观测性
- ✅ 完整的请求/响应日志
- ✅ 结构化日志便于分析
- ✅ 性能监控（响应时间）
- ✅ 错误追踪和诊断

### 2. 一致性
- ✅ 统一的响应格式
- ✅ 统一的异常处理
- ✅ 统一的日志格式
- ✅ 统一的错误码

### 3. 可维护性
- ✅ 减少重复代码
- ✅ 便于调试和排查问题
- ✅ 便于扩展和定制
- ✅ 清晰的代码结构

### 4. 开发效率
- ✅ 快速抛出异常
- ✅ 快速构建响应
- ✅ 自动日志记录
- ✅ 丰富的示例和文档

## 相关文档

- [使用指南](./USAGE_GUIDE.md)
- [后端文档](./README.md)
- [API 文档](http://localhost:8888/docs)
- [更新日志](../CHANGELOG.md)

## 注意事项

1. **日志配置**：首次运行会自动创建 `logs/` 目录
2. **性能影响**：日志记录会增加少量开销，但影响很小
3. **磁盘空间**：日志文件会自动轮转和清理，无需手动管理
4. **敏感信息**：不要在日志中记录密码、Token 等敏感信息
5. **日志级别**：生产环境建议使用 INFO 或 WARNING 级别

## 下一步

- [ ] 添加日志分析工具（ELK、Grafana 等）
- [ ] 添加性能监控（APM）
- [ ] 添加告警机制
- [ ] 添加日志查询 API
- [ ] 添加分布式追踪

---

如有问题或建议，请提交 Issue 或联系项目维护者。
