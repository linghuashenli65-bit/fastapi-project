"""
统一异常处理模块
提供自定义异常类和异常处理器
"""

from typing import Any, Optional, Union

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from backend.core.response import ResponseBuilder
from backend.core.logger import get_logger

logger = get_logger("exceptions")


# ==================== 自定义异常类 ====================

class BaseAPIException(Exception):
    """基础 API 异常"""
    
    def __init__(
        self,
        msg: str,
        code: int = 500,
        data: Any = None
    ):
        self.msg = msg
        self.code = code
        self.data = data
        super().__init__(self.msg)


class BusinessException(BaseAPIException):
    """业务逻辑异常"""
    
    def __init__(
        self,
        msg: str,
        code: int = 400,
        data: Any = None
    ):
        super().__init__(msg, code, data)


class NotFoundException(BaseAPIException):
    """资源不存在异常"""
    
    def __init__(
        self,
        msg: str = "资源不存在",
        resource: str = None,
        data: Any = None
    ):
        if resource:
            msg = f"{resource}不存在"
        super().__init__(msg, 404, data)


class ConflictException(BaseAPIException):
    """资源冲突异常"""
    
    def __init__(
        self,
        msg: str = "资源冲突",
        data: Any = None
    ):
        super().__init__(msg, 409, data)


class ValidationException(BaseAPIException):
    """数据验证异常"""
    
    def __init__(
        self,
        msg: str = "数据验证失败",
        errors: list = None,
        data: Any = None
    ):
        if errors:
            data = errors
        super().__init__(msg, 400, data)


class AuthenticationException(BaseAPIException):
    """认证异常"""
    
    def __init__(
        self,
        msg: str = "认证失败",
        data: Any = None
    ):
        super().__init__(msg, 401, data)


class AuthorizationException(BaseAPIException):
    """授权异常"""
    
    def __init__(
        self,
        msg: str = "无权限访问",
        data: Any = None
    ):
        super().__init__(msg, 403, data)


class DatabaseException(BaseAPIException):
    """数据库异常"""
    
    def __init__(
        self,
        msg: str = "数据库操作失败",
        original_error: Exception = None,
        data: Any = None
    ):
        if original_error:
            msg = f"{msg}: {str(original_error)}"
        super().__init__(msg, 500, data)


class ExternalServiceException(BaseAPIException):
    """外部服务异常"""
    
    def __init__(
        self,
        service_name: str,
        msg: str = None,
        data: Any = None
    ):
        if not msg:
            msg = f"{service_name}服务调用失败"
        super().__init__(msg, 503, data)


class AIException(BaseAPIException):
    """AI 服务异常"""
    
    def __init__(
        self,
        msg: str = "AI 服务调用失败",
        model: str = None,
        data: Any = None
    ):
        if model:
            msg = f"{model}调用失败"
        super().__init__(msg, 500, data)


class RateLimitException(BaseAPIException):
    """频率限制异常"""
    
    def __init__(
        self,
        msg: str = "请求过于频繁，请稍后重试",
        data: Any = None
    ):
        super().__init__(msg, 429, data)


class InvalidParameterException(BaseAPIException):
    """参数异常"""
    
    def __init__(
        self,
        msg: str = "参数错误",
        data: Any = None
    ):
        super().__init__(msg, 400, data)


class DataIntegrityException(BaseAPIException):
    """数据完整性异常"""
    
    def __init__(
        self,
        msg: str = "数据完整性校验失败",
        data: Any = None
    ):
        super().__init__(msg, 400, data)


class DuplicateException(BaseAPIException):
    """数据重复异常"""
    
    def __init__(
        self,
        msg: str = "数据已存在",
        field: str = None,
        data: Any = None
    ):
        if field:
            msg = f"{field}已存在"
        super().__init__(msg, 409, data)


# ==================== 异常处理器 ====================

async def base_api_exception_handler(
    request: Request,
    exc: BaseAPIException
) -> JSONResponse:
    """基础 API 异常处理器"""
    logger.error(
        f"API Exception: {exc.msg}",
        code=exc.code,
        msg=exc.msg,
        data=exc.data,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=exc.code,
        content=ResponseBuilder.error(exc.msg, exc.code, exc.data)
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    """HTTP 异常处理器"""
    logger.error(
        f"HTTP Exception: {exc.detail}",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseBuilder.error(
            msg=str(exc.detail),
            code=exc.status_code
        )
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """请求验证异常处理器"""
    errors = exc.errors()
    error_messages = []
    
    for error in errors:
        loc = "->".join(str(item) for item in error["loc"])
        msg = f"{loc}: {error['msg']}"
        error_messages.append(msg)
    
    logger.warning(
        f"Validation Error: {error_messages}",
        errors=errors,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ResponseBuilder.validation_error(errors, "数据验证失败")
    )


async def pydantic_validation_exception_handler(
    request: Request,
    exc: ValidationError
) -> JSONResponse:
    """Pydantic 验证异常处理器"""
    errors = exc.errors()
    
    logger.warning(
        f"Pydantic Validation Error: {errors}",
        errors=errors,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ResponseBuilder.validation_error(errors, "数据格式错误")
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """通用异常处理器"""
    logger.exception(
        f"Unhandled Exception: {type(exc).__name__}: {str(exc)}",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        path=request.url.path,
        method=request.method,
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ResponseBuilder.error("服务器内部错误", 500)
    )


# ==================== 异常装饰器 ====================

def handle_exceptions(
    default_msg: str = "操作失败",
    default_code: int = 500,
    log_error: bool = True
):
    """
    异常处理装饰器
    
    Args:
        default_msg: 默认错误消息
        default_code: 默认错误码
        log_error: 是否记录错误日志
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except BaseAPIException:
                # 已知的业务异常，直接抛出
                raise
            except Exception as e:
                if log_error:
                    logger.error(
                        f"Exception in {func.__name__}: {type(e).__name__}: {str(e)}",
                        function=func.__name__,
                        exception_type=type(e).__name__,
                        exception_message=str(e),
                        exc_info=True
                    )
                # 转换为业务异常
                raise BaseAPIException(default_msg, default_code)
        
        async_wrapper.__name__ = func.__name__
        async_wrapper.__doc__ = func.__doc__
        return async_wrapper
    return decorator


def async_exception_handler(
    exception_class: type = Exception,
    default_msg: str = "操作失败",
    default_code: int = 500
):
    """
    异步异常处理器装饰器
    
    Args:
        exception_class: 要捕获的异常类
        default_msg: 默认错误消息
        default_code: 默认错误码
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except exception_class as e:
                logger.error(
                    f"Exception in {func.__name__}: {type(e).__name__}: {str(e)}",
                    function=func.__name__,
                    exception_type=type(e).__name__,
                    exception_message=str(e),
                    exc_info=True
                )
                if isinstance(e, BaseAPIException):
                    raise
                raise BaseAPIException(default_msg, default_code)
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator


# ==================== 工具函数 ====================

def raise_not_found(resource: str = None, msg: str = None):
    """抛出资源不存在异常"""
    raise NotFoundException(msg, resource)


def raise_conflict(msg: str = "资源冲突"):
    """抛出资源冲突异常"""
    raise ConflictException(msg)


def raise_validation_error(errors: list = None, msg: str = None):
    """抛出验证异常"""
    raise ValidationException(msg, errors)


def raise_unauthorized(msg: str = "认证失败"):
    """抛出认证异常"""
    raise AuthenticationException(msg)


def raise_forbidden(msg: str = "无权限访问"):
    """抛出授权异常"""
    raise AuthorizationException(msg)


def raise_database_error(error: Exception = None, msg: str = None):
    """抛出数据库异常"""
    raise DatabaseException(msg, error)


def raise_ai_error(msg: str = "AI 服务调用失败", model: str = None):
    """抛出 AI 异常"""
    raise AIException(msg, model)


def raise_duplicate(field: str = None, msg: str = None):
    """抛出数据重复异常"""
    raise DuplicateException(msg, field)


def raise_invalid_parameter(msg: str = "参数错误"):
    """抛出参数异常"""
    raise InvalidParameterException(msg)


__all__ = [
    # 自定义异常类
    "BaseAPIException",
    "BusinessException",
    "NotFoundException",
    "ConflictException",
    "ValidationException",
    "AuthenticationException",
    "AuthorizationException",
    "DatabaseException",
    "ExternalServiceException",
    "AIException",
    "RateLimitException",
    "InvalidParameterException",
    "DataIntegrityException",
    "DuplicateException",
    # 异常处理器
    "base_api_exception_handler",
    "http_exception_handler",
    "validation_exception_handler",
    "pydantic_validation_exception_handler",
    "general_exception_handler",
    # 异常装饰器
    "handle_exceptions",
    "async_exception_handler",
    # 工具函数
    "raise_not_found",
    "raise_conflict",
    "raise_validation_error",
    "raise_unauthorized",
    "raise_forbidden",
    "raise_database_error",
    "raise_ai_error",
    "raise_duplicate",
    "raise_invalid_parameter",
]
