from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from backend.api import agent
from backend.api import auth
from backend.api import class_student
from backend.api import employment
from backend.api import score
from backend.api import student
from backend.api import teacher
from backend.api import users as user_admin
from backend.core.config import settings
from backend.core.exceptions import (
    BaseAPIException,
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    base_api_exception_handler,
)
from backend.core.logger import setup_logger, get_logger
from backend.middlewares.logging_middleware import LoggingMiddleware

# 初始化日志系统
logger = setup_logger(log_level="INFO", app_name="student_management")
app_logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # ---- 启动事件 ----
    frontend_api_base = settings.FRONTEND_API_BASE

    config_file_path = Path(__file__).parent.parent / "static" / "js" / "config.js"
    config_content = f"""// API 基础地址（自动生成，请勿手动修改）
export const API_BASE = '{frontend_api_base}';

// 默认分页参数
export const DEFAULT_PAGE = 1;
export const DEFAULT_SIZE = 10;
"""
    config_file_path.write_text(config_content, encoding="utf-8")
    app_logger.info(f"前端配置文件已生成: API_BASE = {frontend_api_base}")

    # 初始化 fastapi-cache
    from fastapi_cache import FastAPICache
    from fastapi_cache.backends.inmemory import InMemoryBackend
    from fastapi_cache.backends.redis import RedisBackend
    from redis import asyncio as aioredis

    if settings.CACHE_TYPE == "redis":
        redis = aioredis.from_url(settings.CACHE_REDIS_URL, encoding="utf8", decode_responses=True)
        FastAPICache.init(RedisBackend(redis), prefix="sms_cache")
        app_logger.info(f"缓存已初始化: Redis ({settings.CACHE_REDIS_URL})")
    else:
        FastAPICache.init(InMemoryBackend(), prefix="sms_cache")
        app_logger.info("缓存已初始化: InMemory")

    # 初始化语义缓存（L2）
    if settings.SEMANTIC_CACHE_ENABLED:
        try:
            from backend.services.semantic_cache import semantic_cache
            from backend.services.embedding import get_embedding_dim
            await semantic_cache.init(settings.REDIS_STACK_URL)
            if semantic_cache._initialized:
                from backend.utils.helpers import ai_two_level_cache
                ai_two_level_cache.set_l2(semantic_cache)
                app_logger.info(
                    f"语义缓存已初始化: Redis Stack ({settings.REDIS_STACK_URL}), "
                    f"阈值={settings.SEMANTIC_CACHE_THRESHOLD}, "
                    f"维度={get_embedding_dim()}"
                )
        except Exception as e:
            app_logger.warning(f"语义缓存初始化失败，将使用仅L1模式: {e}")

    app_logger.info("=" * 50)
    app_logger.info("学生管理系统启动中...")
    app_logger.info("版本: 1.3.1")
    app_logger.info(f"API 文档: http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}/docs")
    app_logger.info("=" * 50)

    yield  # 应用运行中

    # ---- 关闭事件 ----
    FastAPICache.reset()
    app_logger.info("缓存已清理")

    # 清理语义缓存
    if settings.SEMANTIC_CACHE_ENABLED:
        try:
            from backend.services.semantic_cache import semantic_cache
            await semantic_cache.close()
            app_logger.info("语义缓存已清理")
        except Exception:
            pass

    app_logger.info("学生管理系统已停止")


# 创建 FastAPI 应用
app = FastAPI(
    title="学生管理系统",
    version="1.0.0",
    description="基于 FastAPI 的学生信息管理系统，集成了 AI 智能分析功能",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# 注册CORS中间件（必须在其他中间件之前）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 注册异常处理器
app.add_exception_handler(BaseAPIException, base_api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 注册日志中间件
app.add_middleware(LoggingMiddleware)

# 注册路由
app.include_router(auth.auth_router, tags=["认证模块"])
app.include_router(agent.router, prefix="/agent", tags=["AI模块"])
app.include_router(student.router, prefix="/student", tags=["学生模块"])
app.include_router(teacher.router, prefix="/teacher", tags=["教师模块"])
app.include_router(class_student.router, prefix="/class", tags=["班级模块"])
app.include_router(employment.router, prefix="/employment", tags=["就业模块"])
app.include_router(score.router, prefix="/score", tags=["成绩模块"])
app.include_router(user_admin.router, tags=["用户管理"])

# 获取静态文件目录的绝对路径（相对于 backend/app/main.py）
static_dir = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", tags=["根路径"])
async def root():
    """根路径，返回登录页面"""
    from fastapi.responses import FileResponse
    login_file = static_dir / "login.html"
    return FileResponse(str(login_file))


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "student-management-system",
        "version": "1.0.0"
    }


if __name__ == '__main__':
    uvicorn.run(
        app,
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        log_level="info",
        access_log=False  # 禁用 uvicorn 的访问日志，使用自定义的日志中间件
    )
