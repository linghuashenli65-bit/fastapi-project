"""
用户认证 API 路由 - 基于 fastapi-users
"""
from fastapi import APIRouter

from backend.core.auth import (
    fastapi_users,
    UserRead,
    UserCreate,
    UserUpdate,
    auth_backend,
)

# 创建路由
auth_router = APIRouter()

# 注册/登录路由
auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# 注册路由
auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# 用户验证路由
auth_router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

# 重置密码路由
auth_router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

# 用户管理路由（需要登录）
auth_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# 导出 FastAPIUsers 实例，供其他模块使用
__all__ = ["fastapi_users", "auth_router"]
