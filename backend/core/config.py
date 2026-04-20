# API URL配置（非敏感信息）
QWEN_URL = (
    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
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

    # 缓存配置
    CACHE_TYPE: str = Field(default="memory", description="缓存类型: memory/redis")
    CACHE_REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis连接地址")
    CACHE_DEFAULT_EXPIRE: int = Field(default=300, description="默认缓存过期时间(秒)")
    CACHE_LIST_EXPIRE: int = Field(default=60, description="列表接口缓存过期时间(秒)")
    CACHE_AI_EXPIRE: int = Field(default=600, description="AI查询缓存过期时间(秒)")

    # Redis Stack 语义缓存配置
    REDIS_STACK_URL: str = Field(default="redis://localhost:6379", description="Redis Stack连接地址")
    SEMANTIC_CACHE_ENABLED: bool = Field(default=True, description="是否启用语义缓存")
    SEMANTIC_CACHE_TTL: int = Field(default=3600, description="语义缓存过期时间(秒)")
    SEMANTIC_CACHE_THRESHOLD: float = Field(default=0.85, description="语义相似度阈值(0-1)")
    SEMANTIC_CACHE_TOP_K: int = Field(default=3, description="语义搜索返回最相似的前K条")
    EMBEDDING_MODEL_NAME: str = Field(
        default="shibing624/text2vec-base-chinese",
        description="本地Embedding模型名称(HuggingFace)"
    )

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