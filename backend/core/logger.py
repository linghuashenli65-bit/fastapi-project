"""
统一日志模块
提供统一的日志记录功能
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger


class LoggerConfig:
    """日志配置类"""

    # 日志级别
    LOG_LEVEL = "INFO"
    
    # 日志目录
    LOG_DIR = Path("logs")
    
    # 日志文件格式
    LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    
    # 文件日志格式
    FILE_LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
    
    # 日志文件大小限制 (10 MB)
    LOG_ROTATION = "10 MB"
    
    # 日志文件保留时间 (30 天)
    LOG_RETENTION = "30 days"


def setup_logger(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    app_name: str = "student_management"
):
    """
    配置日志系统
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: 日志目录，默认为 logs/
        app_name: 应用名称，用于日志文件名
    """
    if log_dir is None:
        log_dir = LoggerConfig.LOG_DIR
    
    # 创建日志目录
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 移除默认的 handler
    logger.remove()
    
    # 控制台输出 - 彩色格式
    logger.add(
        sink=lambda msg: print(msg, end=""),
        format=LoggerConfig.LOG_FORMAT,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # 普通日志文件 - 所有级别
    logger.add(
        sink=log_dir / f"{app_name}_{datetime.now().strftime('%Y%m%d')}.log",
        format=LoggerConfig.FILE_LOG_FORMAT,
        level="DEBUG",
        rotation=LoggerConfig.LOG_ROTATION,
        retention=LoggerConfig.LOG_RETENTION,
        encoding="utf-8",
        backtrace=True,
        diagnose=True
    )
    
    # 错误日志文件 - 只记录 ERROR 和 CRITICAL
    logger.add(
        sink=log_dir / f"{app_name}_error_{datetime.now().strftime('%Y%m%d')}.log",
        format=LoggerConfig.FILE_LOG_FORMAT,
        level="ERROR",
        rotation=LoggerConfig.LOG_ROTATION,
        retention=LoggerConfig.LOG_RETENTION,
        encoding="utf-8",
        backtrace=True,
        diagnose=True
    )
    
    return logger


def get_logger(name: str):
    """
    获取指定名称的 logger
    
    Args:
        name: logger 名称
        
    Returns:
        logger 实例
    """
    return logger.bind(name=name)


class APILogger:
    """API 日志记录器"""
    
    def __init__(self, name: str = "api"):
        self.logger = get_logger(name)
    
    async def log_request(self, method: str, path: str, client_ip: str, **kwargs):
        """记录请求"""
        self.logger.info(
            f"Request: {method} {path} from {client_ip}",
            method=method,
            path=path,
            client_ip=client_ip,
            **kwargs
        )
    
    async def log_response(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        **kwargs
    ):
        """记录响应"""
        level = "WARNING" if status_code >= 400 else "INFO"
        self.logger.log(
            level,
            f"Response: {method} {path} - Status: {status_code} - Duration: {duration:.3f}s",
            method=method,
            path=path,
            status_code=status_code,
            duration=duration,
            **kwargs
        )
    
    async def log_error(
        self,
        method: str,
        path: str,
        error: Exception,
        **kwargs
    ):
        """记录错误"""
        self.logger.error(
            f"Error: {method} {path} - {type(error).__name__}: {str(error)}",
            method=method,
            path=path,
            error_type=type(error).__name__,
            error_message=str(error),
            **kwargs,
            exc_info=True
        )


class DBLogger:
    """数据库日志记录器"""
    
    def __init__(self, name: str = "database"):
        self.logger = get_logger(name)
    
    def log_query(self, query: str, params: dict = None, duration: float = None):
        """记录查询"""
        self.logger.debug(
            f"SQL Query: {query[:200]}..." if len(query) > 200 else f"SQL Query: {query}",
            query=query,
            params=params,
            duration=duration
        )
    
    def log_slow_query(self, query: str, duration: float, threshold: float = 1.0):
        """记录慢查询"""
        if duration > threshold:
            self.logger.warning(
                f"Slow Query ({duration:.3f}s > {threshold}s): {query[:200]}...",
                query=query,
                duration=duration,
                threshold=threshold
            )
    
    def log_error(self, error: Exception, query: str = None, params: dict = None):
        """记录数据库错误"""
        self.logger.error(
            f"Database Error: {type(error).__name__}: {str(error)}",
            error_type=type(error).__name__,
            error_message=str(error),
            query=query,
            params=params,
            exc_info=True
        )


class AILogger:
    """AI 日志记录器"""
    
    def __init__(self, name: str = "ai"):
        self.logger = get_logger(name)
    
    def log_request(
        self,
        model: str,
        prompt: str,
        endpoint: str,
        **kwargs
    ):
        """记录 AI 请求"""
        self.logger.info(
            f"AI Request: Model={model}, Endpoint={endpoint}",
            model=model,
            endpoint=endpoint,
            prompt_length=len(prompt),
            **kwargs
        )
    
    def log_response(
        self,
        model: str,
        response_length: int,
        duration: float,
        **kwargs
    ):
        """记录 AI 响应"""
        self.logger.info(
            f"AI Response: Model={model}, Length={response_length}, Duration={duration:.3f}s",
            model=model,
            response_length=response_length,
            duration=duration,
            **kwargs
        )
    
    def log_error(
        self,
        model: str,
        error: Exception,
        **kwargs
    ):
        """记录 AI 错误"""
        self.logger.error(
            f"AI Error: Model={model}, Error={type(error).__name__}: {str(error)}",
            model=model,
            error_type=type(error).__name__,
            error_message=str(error),
            **kwargs,
            exc_info=True
        )


# 创建全局 logger 实例
api_logger = APILogger()
db_logger = DBLogger()
ai_logger = AILogger()

# 导出 logger 供其他模块使用
__all__ = [
    "logger",
    "setup_logger",
    "get_logger",
    "APILogger",
    "DBLogger",
    "AILogger",
    "api_logger",
    "db_logger",
    "ai_logger",
]
