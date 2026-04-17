"""
用户模型 - 基于 fastapi-users
"""
from typing import Optional
from datetime import datetime

from sqlalchemy import Boolean, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable

from backend.core.database import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    """
    用户表模型
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    
    # fastapi-users 基类字段
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # 扩展字段
    username: Mapped[Optional[str]] = mapped_column(String(length=50), nullable=True, unique=True, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(length=100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(length=20), nullable=True)
    
    # 时间戳
    created_at: Mapped[Optional[datetime]] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = mapped_column(default=datetime(1900, 1, 1, 0, 0, 0))
