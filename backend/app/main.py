import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.api import agent
from backend.api import student
from backend.api import teacher
from backend.api import class_student
from backend.api import employment
from backend.api import score
from backend.core.logger import setup_logger, get_logger
from backend.core.exceptions import (
    base_api_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    BaseAPIException,
)
from backend.middlewares.logging_middleware import LoggingMiddleware
from pydantic import ValidationError

# 初始化日志系统
logger = setup_logger(log_level="INFO", app_name="student_management")
app_logger = get_logger("app")

# 创建 FastAPI 应用
app = FastAPI(
    title="学生管理系统",
    version="1.0.0",
    description="基于 FastAPI 的学生信息管理系统，集成了 AI 智能分析功能",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 注册异常处理器
app.add_exception_handler(BaseAPIException, base_api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 注册中间件
app.add_middleware(LoggingMiddleware)

# 注册路由
app.include_router(agent.router, prefix="/agent", tags=["AI模块"])
app.include_router(student.router, prefix="/student", tags=["学生模块"])
app.include_router(teacher.router, prefix="/teacher", tags=["教师模块"])
app.include_router(class_student.router, prefix="/class", tags=["班级模块"])
app.include_router(employment.router, prefix="/employment", tags=["就业模块"])
app.include_router(score.router, prefix="/score", tags=["成绩模块"])

# 获取静态文件目录的绝对路径（相对于 backend/app/main.py）
static_dir = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", tags=["根路径"])
async def root():
    """根路径，返回静态页面"""
    from fastapi.responses import FileResponse
    index_file = static_dir / "index.html"
    return FileResponse(str(index_file))


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "student-management-system",
        "version": "1.0.0"
    }


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    app_logger.info("=" * 50)
    app_logger.info("学生管理系统启动中...")
    app_logger.info("版本: 1.0.0")
    app_logger.info("API 文档: http://127.0.0.1:8888/docs")
    app_logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    app_logger.info("学生管理系统已停止")


if __name__ == '__main__':
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8888,
        log_level="info",
        access_log=False  # 禁用 uvicorn 的访问日志，使用自定义的日志中间件
    )
