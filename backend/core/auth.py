"""
FastAPI-Users 认证配置
"""
from typing import AsyncGenerator, Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, schemas, FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from backend.core.config import settings
from backend.core.database import AsyncSessionLocal, get_async_db
from backend.models.user import User


# ==================== 用户 Schema ====================
class UserRead(schemas.BaseUser[int]):
    """用户读取 Schema"""
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(schemas.BaseUserCreate):
    """用户创建 Schema"""
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserUpdate(schemas.BaseUserUpdate):
    """用户更新 Schema"""
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None


# ==================== JWT 认证策略 ====================
def get_jwt_strategy() -> JWTStrategy:
    """
    获取 JWT 认证策略
    """
    # 从配置中读取 SECRET_KEY，默认使用一个安全的随机密钥
    secret = getattr(settings, 'SECRET_KEY', 'your-secret-key-change-this-in-production')
    
    return JWTStrategy(secret=secret, lifetime_seconds=3600 * 24 * 7)  # 7天过期


# ==================== 认证后端 ====================
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


# ==================== 用户管理器 ====================
class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """
    自定义用户管理器
    """
    reset_password_token_secret = settings.SECRET_KEY if hasattr(settings, 'SECRET_KEY') else 'your-secret-key'
    verification_token_secret = settings.SECRET_KEY if hasattr(settings, 'SECRET_KEY') else 'your-secret-key'
    
    async def on_after_register(self, user: User, request: Request | None = None):
        """
        注册后的回调
        """
        print(f"User {user.id} has registered.")
    
    async def on_after_forgot_password(self, user: User, token: str, request: Request | None = None):
        """
        忘记密码后的回调
        """
        print(f"User {user.id} has forgot their password. Reset token: {token}")
    
    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        """
        请求邮箱验证后的回调
        """
        print(f"Verification requested for user {user.id}. Verification token: {token}")


# ==================== 数据库访问对象 ====================
async def get_user_db(session: AsyncSessionLocal = Depends(get_async_db)) -> AsyncGenerator:
    """
    获取用户数据库会话
    """
    from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
    
    yield SQLAlchemyUserDatabase(session, User)


# ==================== 依赖注入 ====================
async def get_user_manager(user_db=Depends(get_user_db)):
    """
    获取用户管理器
    """
    yield UserManager(user_db)


# ==================== 用户认证依赖 ====================
# 创建 FastAPIUsers 实例（必须在 auth.py 之前）
fastapi_users = FastAPIUsers(get_user_manager, [auth_backend])


async def get_current_active_user(
    user: User = Depends(fastapi_users.current_user(active=True))
) -> User:
    return user


async def get_current_active_superuser(
    user: User = Depends(fastapi_users.current_user(active=True, superuser=True))
) -> User:
    return user


# 别名
current_active_user = Depends(get_current_active_user)
current_active_superuser = Depends(get_current_active_superuser)
