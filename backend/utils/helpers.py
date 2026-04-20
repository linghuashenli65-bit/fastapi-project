# backend/utils/helpers.py
import re
import hashlib
import json
from typing import Any, Optional

from fastapi import Request


def clean_ai_response(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    # 去除开头的 ``` 及可选的 language（如 json, sql），以及结尾的 ```
    text = re.sub(r'^```(?:[a-zA-Z0-9_]*)?\s*\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\n?```$', '', text)
    return text.strip()


def cache_key_builder(func, namespace: str = "", *, request: Request = None, **kwargs):
    """
    自定义缓存键构建器，排除不可序列化的依赖注入参数（如 db、request、response）
    只使用路径参数和查询参数构建缓存键
    """
    # 过滤掉不可序列化的参数
    filtered = {}
    for k, v in kwargs.items():
        if k in ("db", "request", "response"):
            continue
        # 跳过 SQLAlchemy 会话等对象
        if hasattr(v, "__tablename__") or hasattr(type(v), "__tablename__"):
            continue
        # 跳过非基本类型（如 Pydantic 模型、DB session 等）
        if isinstance(v, (str, int, float, bool, type(None))):
            filtered[k] = v
        elif isinstance(v, (list, tuple, set)):
            filtered[k] = list(v)
        elif isinstance(v, dict):
            filtered[k] = v

    raw = json.dumps(filtered, sort_keys=True, default=str)
    key = hashlib.md5(raw.encode()).hexdigest()
    prefix = namespace or func.__module__
    return f"{prefix}:{func.__name__}:{key}"


class TTLCache:
    """简单的带过期时间的内存缓存"""

    def __init__(self, maxsize: int = 256, default_ttl: int = 600):
        self._cache: dict = {}
        self._maxsize = maxsize
        self._default_ttl = default_ttl

    def _make_key(self, *args, **kwargs) -> str:
        raw = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        import time
        entry = self._cache.get(key)
        if entry is None:
            return None
        if time.time() > entry["expire"]:
            del self._cache[key]
            return None
        return entry["value"]

    def set(self, key: str, value: Any, ttl: int = None):
        import time
        if len(self._cache) >= self._maxsize:
            # 淘汰最旧的条目
            oldest_key = min(self._cache, key=lambda k: self._cache[k]["expire"])
            del self._cache[oldest_key]
        self._cache[key] = {"value": value, "expire": time.time() + (ttl or self._default_ttl)}

    def cached(self, ttl: int = None):
        """装饰器：缓存异步函数的结果"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                key = self._make_key(func.__name__, *args, **kwargs)
                result = self.get(key)
                if result is not None:
                    return result
                result = await func(*args, **kwargs)
                self.set(key, result, ttl)
                return result
            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            return wrapper
        return decorator


# 全局 AI 缓存实例
ai_cache = TTLCache(maxsize=128, default_ttl=600)


class AITwoLevelCache:
    """
    AI 两级缓存：
    L1 - TTLCache：内存精确匹配，毫秒级
    L2 - SemanticCache：Redis Stack 语义搜索，秒级
    """

    def __init__(self, l1: TTLCache):
        self.l1 = l1
        self.l2 = None  # SemanticCache 实例，lifespan 中注入
        self._l2_enabled = False

    def set_l2(self, semantic_cache):
        """注入 L2 语义缓存实例"""
        self.l2 = semantic_cache
        self._l2_enabled = True

    def disable_l2(self):
        """禁用 L2（Redis 不可用时降级）"""
        self._l2_enabled = False

    def cached(self, ttl: int = 600):
        """装饰器：两级缓存异步函数结果"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # L1 精确匹配
                key = self.l1._make_key(func.__name__, *args, **kwargs)
                result = self.l1.get(key)
                if result is not None:
                    return result

                # L2 语义搜索
                if self._l2_enabled and self.l2 is not None:
                    query = kwargs.get("query", args[0] if args else "")
                    model = kwargs.get("model", "")
                    try:
                        l2_result = await self.l2.search(query, model)
                        if l2_result is not None:
                            # 回填 L1
                            self.l1.set(key, l2_result, ttl)
                            return l2_result
                    except Exception as e:
                        import logging
                        logging.getLogger("ai_cache").warning(f"L2 语义缓存查询失败，降级为直连: {e}")
                        self._l2_enabled = False

                # 调用实际函数
                result = await func(*args, **kwargs)

                # 写入 L1
                self.l1.set(key, result, ttl)

                # 写入 L2
                if self._l2_enabled and self.l2 is not None:
                    try:
                        query = kwargs.get("query", args[0] if args else "")
                        model = kwargs.get("model", "")
                        await self.l2.store(query, model, result)
                    except Exception:
                        pass  # L2 写入失败不影响结果

                return result
            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            return wrapper
        return decorator


# 全局两级缓存实例
ai_two_level_cache = AITwoLevelCache(ai_cache)