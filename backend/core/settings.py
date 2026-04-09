# 统一配置读取
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    # 项目基础信息
    PROJECT_NAME: str
    API_PREFIX: str
    BACKEND_HOST: str
    BACKEND_PORT: int

    # 数据库
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # 日志配置
    LOG_LEVEL: str
    LOG_FILE: str
    LOG_FORMAT: str

    # ========== 新增：认证白名单 ==========
    # 无需登录即可访问的接口路径
    AUTH_WHITELIST: List = [
        "/",  # 首页
        "/docs",  # 接口文档
        "/redoc",
        "/openapi.json",  # <--- 关键！必须加
        "/user/login",  # 登录
        "/user/register",  # 注册
        "/user/",  # 新增查询
        "/static/login.html" #登录页面
    ]

    # 20260404 zws
    # 新增3行 ！！！强密钥！！！
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # 从 .env 文件加载
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# 全局唯一配置实例
settings = Settings()