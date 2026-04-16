# API URL配置（非敏感信息）
QWEN_URL = (
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
)
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

# 获取项目根目录（backend/core/config.py -> backend/ -> 项目根目录）
PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    # 项目基础配置
    PROJECT_NAME: str = Field(default="Student Management System")
    API_PREFIX: str = Field(default="/api/v1")
    BACKEND_HOST: str = Field(default="127.0.0.1")
    BACKEND_PORT: int = Field(default=8000)

    # 数据库配置
    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=3306)
    DB_USER: str = Field(default="root")
    DB_PASSWORD: str = Field(default="")
    DB_NAME: str = Field(default="student_management_system")

    # 日志配置
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: str = Field(default="logs/app.log")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # JWT 配置
    SECRET_KEY: str = Field(default="")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)

    # 大模型API配置
    QWEN_API_KEY: str = Field(default="")
    DEEPSEEK_API_KEY: str = Field(default="")

    # 前端配置
    FRONTEND_API_BASE: str = Field(default="http://localhost:8000")

    # 认证白名单（无需登录即可访问的接口路径）
    AUTH_WHITELIST: list = Field(default_factory=lambda: [
        "/",  # 首页
        "/docs",  # 接口文档
        "/redoc",
        "/openapi.json",
        "/user/login",  # 登录
        "/user/register",  # 注册
        "/user/",  # 查询
        "/static/login.html"  # 登录页面
    ])

    # CORS配置
    CORS_ORIGINS: list = Field(default_factory=lambda: ["*"])
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    CORS_ALLOW_METHODS: list = Field(default_factory=lambda: ["*"])
    CORS_ALLOW_HEADERS: list = Field(default_factory=lambda: ["*"])

    # 生成数据库 URL
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        # 使用项目根目录的 .env 文件
        env_file = PROJECT_ROOT / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # 忽略额外的环境变量


settings = Settings()

# API配置（统一格式）
API_CONFIG = {
    "qwen": {
        "url": QWEN_URL,
        "api_key": settings.QWEN_API_KEY,
        "model": "qwen-max"
    },
    "deepseek": {
        "url": DEEPSEEK_URL,
        "api_key": settings.DEEPSEEK_API_KEY,
        "model": "deepseek-chat"
    }
}