import httpx
from backend.core.config import API_CONFIG


class LLMAPIError(Exception):
    """LLM API 调用异常"""
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error


async def call_qwen(prompt: str) -> str:
    """
    调用通义千问API（OpenAI兼容格式）
    DashScope兼容模式：与OpenAI格式一致
    抛出 LLMAPIError 异常而非返回空字符串
    """
    try:
        async with httpx.AsyncClient(timeout=60.0, proxy=None) as client:
            response = await client.post(
                API_CONFIG["qwen"]["url"],
                json={
                    "model": API_CONFIG["qwen"]["model"],
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                },
                headers={
                    "Authorization": f"Bearer {API_CONFIG['qwen']['api_key']}",
                    "Content-Type": "application/json"
                }
            )
            # 检查响应状态码
            if response.status_code != 200:
                error_msg = f"调用Qwen API失败: HTTP {response.status_code}, 响应: {response.text[:200]}"
                raise LLMAPIError(error_msg)

            result = response.json()
            # OpenAI兼容格式
            if "choices" in result and result["choices"]:
                return result["choices"][0]["message"]["content"]
            else:
                raise LLMAPIError(f"调用Qwen API失败: 响应格式错误，缺少 choices 字段: {result}")
    except httpx.ConnectError as e:
        raise LLMAPIError(f"Qwen API 连接失败，请检查网络和代理设置: {e}", e)
    except httpx.TimeoutException as e:
        raise LLMAPIError(f"Qwen API 请求超时: {e}", e)
    except httpx.RemoteProtocolError as e:
        raise LLMAPIError(f"Qwen API 服务器断开连接: {e}", e)
    except LLMAPIError:
        raise  # 重新抛出自定义异常
    except Exception as e:
        raise LLMAPIError(f"调用Qwen API时发生未知错误: {e}", e)


async def call_deepseek(prompt: str) -> str:
    """
    调用DeepSeek API
    抛出 LLMAPIError 异常而非返回空字符串
    """
    try:
        async with httpx.AsyncClient(timeout=60.0, proxy=None) as client:
            response = await client.post(
                API_CONFIG["deepseek"]["url"],
                json={
                    "model": API_CONFIG["deepseek"]["model"],
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                },
                headers={
                    "Authorization": f"Bearer {API_CONFIG['deepseek']['api_key']}",
                    "Content-Type": "application/json"
                }
            )
            # 检查响应状态码
            if response.status_code != 200:
                error_msg = f"调用DeepSeek API失败: HTTP {response.status_code}, 响应: {response.text[:200]}"
                raise LLMAPIError(error_msg)

            result = response.json()
            # 检查响应格式
            if "choices" not in result or not result["choices"]:
                raise LLMAPIError(f"调用DeepSeek API失败: 响应格式错误，缺少 choices 字段: {result}")

            return result["choices"][0]["message"]["content"]
    except httpx.ConnectError as e:
        raise LLMAPIError(f"DeepSeek API 连接失败，请检查网络和代理设置: {e}", e)
    except httpx.TimeoutException as e:
        raise LLMAPIError(f"DeepSeek API 请求超时: {e}", e)
    except httpx.RemoteProtocolError as e:
        raise LLMAPIError(f"DeepSeek API 服务器断开连接: {e}", e)
    except LLMAPIError:
        raise  # 重新抛出自定义异常
    except Exception as e:
        raise LLMAPIError(f"调用DeepSeek API时发生未知错误: {e}", e)
