QWEN_API_KEY = "sk-15c2dda65e8145159ac4b13e8955c1b2"
QWEN_URL = (
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
)
DEEPSEEK_API_KEY = "sk-8d9aa2531dcf4490a84b705b89f93fff"
DEEPSEEK_URL="https://api.deepseek.com/v1/chat/completions"

# MySQL配置
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "8312460",
    "database": "student_management_system",
}
from pydantic_settings import BaseSettings
from pydantic import Field


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
    DB_PASSWORD: str = Field(default="8312460")
    DB_NAME: str = Field(default="student_management_system")

    # 日志配置
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: str = Field(default="logs/app.log")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # JWT 配置
    secret_key: str = Field(default="your-secret-key-change-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)

    # 生成数据库 URL
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"  # 从项目根目录的 .env 文件读取
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # 忽略额外的环境变量


settings = Settings()