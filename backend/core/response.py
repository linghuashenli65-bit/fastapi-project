"""
统一响应模块
提供统一的 API 响应格式
"""

from typing import Any, Optional, Generic, TypeVar, List

from pydantic import BaseModel, Field

# 泛型类型变量
T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """
    统一响应模型
    
    成功响应格式:
    {
        "code": 200,
        "msg": "success",
        "data": {...}
    }
    
    失败响应格式:
    {
        "code": 400,
        "msg": "error message",
        "data": null
    }
    """
    
    code: int = Field(description="响应状态码")
    msg: str = Field(description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")


class SuccessResponse(ResponseModel[T]):
    """成功响应"""
    
    def __init__(
        self,
        data: Optional[T] = None,
        msg: str = "success",
        code: int = 200
    ):
        super().__init__(code=code, msg=msg, data=data)


class ErrorResponse(BaseModel):
    """错误响应模型"""
    
    code: int = Field(description="错误状态码")
    msg: str = Field(description="错误消息")
    data: Optional[Any] = Field(default=None, description="错误详情数据")
    
    def __init__(
        self,
        msg: str,
        code: int = 500,
        data: Optional[Any] = None
    ):
        super().__init__(code=code, msg=msg, data=data)


class PaginationResponse(BaseModel):
    """分页响应模型"""
    
    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="success", description="响应消息")
    data: List[Any] = Field(default_factory=list, description="数据列表")
    count: int = Field(default=0, description="总记录数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页大小")
    total_pages: int = Field(default=0, description="总页数")
    
    @classmethod
    def create(
        cls,
        data: List[Any],
        count: int,
        page: int = 1,
        page_size: int = 10,
        msg: str = "success"
    ) -> "PaginationResponse":
        """
        创建分页响应
        
        Args:
            data: 数据列表
            count: 总记录数
            page: 当前页码
            page_size: 每页大小
            msg: 响应消息
            
        Returns:
            PaginationResponse 实例
        """
        total_pages = (count + page_size - 1) // page_size
        return cls(
            code=200,
            msg=msg,
            data=data,
            count=count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )


class DetailResponse(BaseModel):
    """详情响应模型"""
    
    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="success", description="响应消息")
    data: Optional[Any] = Field(default=None, description="详情数据")


class BatchResponse(BaseModel):
    """批量操作响应模型"""
    
    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="success", description="响应消息")
    data: Optional[BatchOperationData] = Field(default=None, description="批量操作数据")


class BatchOperationData(BaseModel):
    """批量操作数据"""
    
    success_count: int = Field(description="成功数量")
    failed_count: int = Field(description="失败数量")
    failed_items: List[Any] = Field(default_factory=list, description="失败项列表")
    errors: List[str] = Field(default_factory=list, description="错误信息列表")


class DeleteResponse(BaseModel):
    """删除响应模型"""
    
    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="删除成功", description="响应消息")
    data: Optional[dict] = Field(default=None, description="删除数据")


class CreateResponse(BaseModel):
    """创建响应模型"""
    
    code: int = Field(default=201, description="状态码")
    msg: str = Field(default="创建成功", description="响应消息")
    data: Optional[Any] = Field(default=None, description="创建的数据")


class UpdateResponse(BaseModel):
    """更新响应模型"""
    
    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="更新成功", description="响应消息")
    data: Optional[Any] = Field(default=None, description="更新后的数据")


class ValidationResponse(BaseModel):
    """验证响应模型"""
    
    code: int = Field(default=400, description="状态码")
    msg: str = Field(default="验证失败", description="响应消息")
    errors: List[dict] = Field(default_factory=list, description="验证错误列表")


class AIResponse(BaseModel):
    """AI 响应模型"""
    
    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="success", description="响应消息")
    data: Optional[dict] = Field(default=None, description="AI 响应数据")
    
    # SQL 查询特定字段
    sql: Optional[str] = Field(default=None, description="生成的 SQL")
    query_data: Optional[List[dict]] = Field(default=None, description="查询结果")
    
    # 分析特定字段
    charts: Optional[List[dict]] = Field(default=None, description="图表数据")
    analysis: Optional[str] = Field(default=None, description="分析文本")


class StreamResponse(BaseModel):
    """流式响应模型"""
    
    stage: str = Field(description="当前阶段")
    percent: Optional[float] = Field(default=None, description="进度百分比")
    message: Optional[str] = Field(default=None, description="进度消息")
    data: Optional[Any] = Field(default=None, description="阶段数据")


# 响应构建器类
class ResponseBuilder:
    """响应构建器"""
    
    @staticmethod
    def success(
        data: Any = None,
        msg: str = "success",
        code: int = 200
    ) -> dict:
        """
        构建成功响应
        
        Args:
            data: 响应数据
            msg: 响应消息
            code: 状态码
            
        Returns:
            响应字典
        """
        return {
            "code": code,
            "msg": msg,
            "data": data
        }
    
    @staticmethod
    def error(
        msg: str,
        code: int = 500,
        data: Any = None
    ) -> dict:
        """
        构建错误响应
        
        Args:
            msg: 错误消息
            code: 状态码
            data: 错误详情数据
            
        Returns:
            响应字典
        """
        return {
            "code": code,
            "msg": msg,
            "data": data
        }
    
    @staticmethod
    def pagination(
        data: List[Any],
        count: int,
        page: int = 1,
        page_size: int = 10,
        msg: str = "success"
    ) -> dict:
        """
        构建分页响应
        
        Args:
            data: 数据列表
            count: 总记录数
            page: 当前页码
            page_size: 每页大小
            msg: 响应消息
            
        Returns:
            响应字典
        """
        total_pages = (count + page_size - 1) // page_size
        return {
            "code": 200,
            "msg": msg,
            "data": data,
            "count": count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    @staticmethod
    def created(
        data: Any = None,
        msg: str = "创建成功"
    ) -> dict:
        """
        构建创建成功响应
        
        Args:
            data: 创建的数据
            msg: 响应消息
            
        Returns:
            响应字典
        """
        return {
            "code": 201,
            "msg": msg,
            "data": data
        }
    
    @staticmethod
    def updated(
        data: Any = None,
        msg: str = "更新成功"
    ) -> dict:
        """
        构建更新成功响应
        
        Args:
            data: 更新后的数据
            msg: 响应消息
            
        Returns:
            响应字典
        """
        return {
            "code": 200,
            "msg": msg,
            "data": data
        }
    
    @staticmethod
    def deleted(
        msg: str = "删除成功"
    ) -> dict:
        """
        构建删除成功响应
        
        Args:
            msg: 响应消息
            
        Returns:
            响应字典
        """
        return {
            "code": 200,
            "msg": msg,
            "data": None
        }
    
    @staticmethod
    def validation_error(
        errors: List[dict],
        msg: str = "验证失败"
    ) -> dict:
        """
        构建验证错误响应
        
        Args:
            errors: 验证错误列表
            msg: 响应消息
            
        Returns:
            响应字典
        """
        return {
            "code": 400,
            "msg": msg,
            "data": errors
        }
    
    @staticmethod
    def not_found(
        msg: str = "资源不存在",
        resource: str = None
    ) -> dict:
        """
        构建资源不存在响应
        
        Args:
            msg: 响应消息
            resource: 资源名称
            
        Returns:
            响应字典
        """
        if resource:
            msg = f"{resource}不存在"
        return {
            "code": 404,
            "msg": msg,
            "data": None
        }
    
    @staticmethod
    def unauthorized(
        msg: str = "未授权"
    ) -> dict:
        """
        构建未授权响应
        
        Args:
            msg: 响应消息
            
        Returns:
            响应字典
        """
        return {
            "code": 401,
            "msg": msg,
            "data": None
        }
    
    @staticmethod
    def forbidden(
        msg: str = "无权限"
    ) -> dict:
        """
        构建无权限响应
        
        Args:
            msg: 响应消息
            
        Returns:
            响应字典
        """
        return {
            "code": 403,
            "msg": msg,
            "data": None
        }
    
    @staticmethod
    def conflict(
        msg: str = "资源冲突"
    ) -> dict:
        """
        构建资源冲突响应
        
        Args:
            msg: 响应消息
            
        Returns:
            响应字典
        """
        return {
            "code": 409,
            "msg": msg,
            "data": None
        }


# 导出常用函数
def success(data=None, msg="success", code=200):
    """成功响应"""
    return ResponseBuilder.success(data, msg, code)


def error(msg, code=500, data=None):
    """错误响应"""
    return ResponseBuilder.error(msg, code, data)


def pagination(data, count, page=1, page_size=10, msg="success"):
    """分页响应"""
    return ResponseBuilder.pagination(data, count, page, page_size, msg)


def created(data=None, msg="创建成功"):
    """创建成功响应"""
    return ResponseBuilder.created(data, msg)


def updated(data=None, msg="更新成功"):
    """更新成功响应"""
    return ResponseBuilder.updated(data, msg)


def deleted(msg="删除成功"):
    """删除成功响应"""
    return ResponseBuilder.deleted(msg)


def not_found(msg="资源不存在"):
    """资源不存在响应"""
    return ResponseBuilder.not_found(msg)


__all__ = [
    "ResponseModel",
    "SuccessResponse",
    "ErrorResponse",
    "PaginationResponse",
    "DetailResponse",
    "BatchResponse",
    "BatchOperationData",
    "DeleteResponse",
    "CreateResponse",
    "UpdateResponse",
    "ValidationResponse",
    "AIResponse",
    "StreamResponse",
    "ResponseBuilder",
    "success",
    "error",
    "pagination",
    "created",
    "updated",
    "deleted",
    "not_found",
]
