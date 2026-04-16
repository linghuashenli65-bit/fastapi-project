"""
日志中间件
记录所有请求和响应
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.core.logger import api_logger, get_logger

logger = get_logger("middleware")


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        # 记录请求开始时间
        start_time = time.time()
        
        # 提取客户端 IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 提取请求头中的真实 IP（如果通过代理）
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        # 记录请求
        await api_logger.log_request(
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
            query_params=str(request.query_params),
            headers=dict(request.headers)
        )
        
        # 处理请求
        try:
            response = await call_next(request)
        except Exception as e:
            # 记录异常
            await api_logger.log_error(
                method=request.method,
                path=request.url.path,
                error=e
            )
            raise
        
        # 计算处理时间
        duration = time.time() - start_time
        
        # 添加响应头
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        response.headers["X-Request-ID"] = self._generate_request_id()
        
        # 记录响应
        await api_logger.log_response(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=duration
        )
        
        return response
    
    def _generate_request_id(self) -> str:
        """生成请求 ID"""
        import uuid
        return str(uuid.uuid4())


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """错误日志中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        try:
            return await call_next(request)
        except Exception as e:
            # 记录错误
            logger.error(
                f"Unhandled error in {request.method} {request.url.path}",
                exception_type=type(e).__name__,
                exception_message=str(e),
                path=request.url.path,
                method=request.method,
                exc_info=True
            )
            # 重新抛出异常，让其他中间件处理
            raise


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件（简化版）"""
    
    def __init__(self, app: ASGIApp, *, log_level: str = "INFO"):
        super().__init__(app)
        self.log_level = log_level
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        start_time = time.time()
        
        # 记录请求
        logger.log(
            self.log_level,
            f"{request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}"
        )
        
        # 处理请求
        response = await call_next(request)
        
        # 记录响应
        duration = time.time() - start_time
        logger.log(
            self.log_level,
            f"{request.method} {request.url.path} - Status: {response.status_code} - Duration: {duration:.3f}s"
        )
        
        return response


__all__ = [
    "LoggingMiddleware",
    "ErrorLoggingMiddleware",
    "RequestLoggingMiddleware",
]
