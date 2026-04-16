"""
生成前端配置文件的脚本
从环境变量读取配置，生成前端需要的配置文件
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def generate_frontend_config():
    """生成前端配置文件"""
    # 获取配置
    backend_host = os.getenv("BACKEND_HOST", "localhost")
    backend_port = os.getenv("BACKEND_PORT", "8000")
    frontend_api_base = os.getenv("FRONTEND_API_BASE", f"http://{backend_host}:{backend_port}")

    # 前端配置文件路径
    config_file_path = Path(__file__).parent.parent / "backend" / "static" / "js" / "config.js"

    # 生成配置内容
    config_content = f"""// API 基础地址（自动生成，请勿手动修改）
export const API_BASE = '{frontend_api_base}';

// 默认分页参数
export const DEFAULT_PAGE = 1;
export const DEFAULT_SIZE = 10;
"""

    # 写入配置文件
    config_file_path.write_text(config_content, encoding="utf-8")
    print(f"前端配置文件已生成: {config_file_path}")
    print(f"API_BASE: {frontend_api_base}")

if __name__ == "__main__":
    generate_frontend_config()
