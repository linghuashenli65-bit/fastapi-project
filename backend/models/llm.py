import httpx
from backend.core.config import API_CONFIG


async def call_qwen(prompt: str) -> str:
    """
    调用通义千问API
    通义千问API格式：
    - 请求：{"model": "qwen-max", "input": {"messages": [...]}, "parameters": {...}}
    - 响应：{"output": {"text": "..."}, "usage": {...}}
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                API_CONFIG["qwen"]["url"],
                json={
                    "model": API_CONFIG["qwen"]["model"],
                    "input": {
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    },
                    "parameters": {
                        "temperature": 0.7
                    }
                },
                headers={
                    "Authorization": f"Bearer {API_CONFIG['qwen']['api_key']}",
                    "Content-Type": "application/json"
                }
            )
            # 检查响应状态码
            if response.status_code != 200:
                print(f"调用Qwen API失败: HTTP {response.status_code}")
                print(f"响应内容: {response.text}")
                return ""

            result = response.json()
            # 检查响应格式（通义千问格式）
            if "output" in result and "text" in result["output"]:
                return result["output"]["text"]
            # 兼容可能的 OpenAI 格式
            elif "choices" in result:
                return result["choices"][0]["message"]["content"]
            else:
                print(f"调用Qwen API失败: 响应格式错误")
                print(f"响应内容: {result}")
                return ""
    except Exception as e:
        print(f"调用Qwen API失败: {e}")
        import traceback
        traceback.print_exc()
        return ""


async def call_deepseek(prompt: str) -> str:
    """
    调用DeepSeek API
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
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
                print(f"调用DeepSeek API失败: HTTP {response.status_code}")
                print(f"响应内容: {response.text}")
                return ""

            result = response.json()
            # 检查响应格式
            if "choices" not in result:
                print(f"调用DeepSeek API失败: 响应格式错误，缺少 'choices' 字段")
                print(f"响应内容: {result}")
                return ""

            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"调用DeepSeek API失败: {e}")
        import traceback
        traceback.print_exc()
        return ""
