"""
语义搜索缓存：基于 Redis Stack 的向量搜索实现 AI 查询结果的语义级缓存

架构：
- 文档存储：Redis JSON
- 向量搜索：RediSearch + FLAT 索引
- 索引键前缀：semantic_cache:
- 索引名称：idx:semantic_cache
"""
import time
import uuid
from datetime import date, datetime
from typing import Any, Optional

import numpy as np
import redis.asyncio as aioredis

from backend.core.config import settings
from backend.core.logger import get_logger
from backend.services.embedding import get_embedding, get_embedding_dim

logger = get_logger("semantic_cache")


def _serialize_for_json(obj: Any) -> Any:
    """
    递归序列化对象以适配 JSON，包含：
    - datetime/date 转换为 ISO 字符串
    - bytes 转换为 base64 字符串
    - 递归处理 dict/list/tuple
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    elif isinstance(obj, dict):
        return {k: _serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_serialize_for_json(item) for item in obj]
    else:
        return obj


class SemanticCache:
    """基于 Redis Stack 的语义搜索缓存"""

    PREFIX = "semantic_cache:"
    INDEX_NAME = "idx:semantic_cache"

    def __init__(self):
        self.redis: aioredis.Redis | None = None
        self._initialized = False

    async def init(self, redis_url: str):
        """初始化 Redis 连接和搜索索引"""
        try:
            self.redis = aioredis.from_url(redis_url, decode_responses=True)
            # 测试连接
            await self.redis.ping()
            logger.info(f"SemanticCache: Redis 连接成功 ({redis_url})")

            # 创建搜索索引
            await self._create_index()
            self._initialized = True
            logger.info("SemanticCache: 索引初始化完成")
        except Exception as e:
            logger.warning(f"SemanticCache: 初始化失败，语义缓存将不可用 - {e}")
            self._initialized = False

    async def _create_index(self):
        """创建搜索索引（如果不存在）"""
        from redis.commands.search.field import TextField, VectorField, NumericField, TagField
        from redis.commands.search.index_definition import IndexDefinition, IndexType

        try:
            # 检查索引是否已存在
            await self.redis.ft(self.INDEX_NAME).info()
            logger.info(f"SemanticCache: 索引 {self.INDEX_NAME} 已存在")
            return
        except Exception:
            pass  # 索引不存在，继续创建

        dim = get_embedding_dim()
        try:
            schema = (
                TextField("$.query", as_name="query"),
                VectorField(
                    "$.query_vector",
                    "FLAT",
                    {
                        "TYPE": "FLOAT32",
                        "DIM": dim,
                        "DISTANCE_METRIC": "COSINE",
                        "INITIAL_CAP": 1000,
                    },
                    as_name="query_vector",
                ),
                TagField("$.model", as_name="model"),
                NumericField("$.created_at", as_name="created_at"),
            )
            definition = IndexDefinition(prefix=[self.PREFIX], index_type=IndexType.JSON)
            await self.redis.ft(self.INDEX_NAME).create_index(
                fields=schema,
                definition=definition,
            )
            logger.info(f"SemanticCache: 索引创建成功 (dim={dim})")
        except Exception as e:
            err_msg = str(e)
            if "already exists" in err_msg:
                logger.info(f"SemanticCache: 索引 {self.INDEX_NAME} 已存在（并发创建）")
                return
            logger.error(f"SemanticCache: 索引创建失败 - {e}")
            raise

    async def search(
        self,
        query: str,
        threshold: float | None = None,
    ) -> Optional[dict]:
        """
        语义搜索缓存

        Args:
            query: 用户查询文本
            threshold: 相似度阈值，None 则使用配置值

        Returns:
            命中的缓存结果，未命中返回 None
        """
        if not self._initialized or self.redis is None:
            return None

        threshold = threshold or settings.SEMANTIC_CACHE_THRESHOLD
        top_k = settings.SEMANTIC_CACHE_TOP_K

        try:
            from redis.commands.search.query import Query

            # 生成查询向量
            query_vector = get_embedding(query)
            vector_bytes = np.array(query_vector, dtype=np.float32).tobytes()

            # 构建搜索查询：KNN 搜索（不按模型过滤，不同模型共享缓存）
            base_query = f"*=>[KNN {top_k} @query_vector $vec AS score]"
            q = Query(base_query).sort_by("score").dialect(2)

            results = await self.redis.ft(self.INDEX_NAME).search(
                q, query_params={"vec": vector_bytes}
            )

            if not results.docs:
                return None

            # 遍历结果，找到第一个满足相似度阈值且未过期的
            now = time.time()
            for doc in results.docs:
                # KNN 返回的 score 是距离（1 - cosine_similarity），需要转换
                distance = float(doc.score)
                similarity = 1.0 - distance

                if similarity < threshold:
                    continue

                # 读取完整文档检查过期
                doc_key = doc.id
                raw = await self.redis.json().get(doc_key)
                if raw is None:
                    continue

                # 检查是否过期
                created_at = raw.get("created_at", 0)
                ttl = raw.get("ttl", settings.SEMANTIC_CACHE_TTL)
                if now - created_at > ttl:
                    # 已过期，删除
                    await self.redis.delete(doc_key)
                    continue

                logger.info(
                    f"SemanticCache: 命中 (similarity={similarity:.4f}, "
                    f"query='{raw.get('query', '')}')"
                )
                return raw.get("result")

            return None

        except Exception as e:
            logger.warning(f"SemanticCache: 搜索异常 - {e}")
            return None

    async def store(
        self,
        query: str,
        model: str,
        result: Any,
        ttl: int | None = None,
    ) -> Optional[str]:
        """
        存储查询结果到语义缓存

        Args:
            query: 用户查询文本
            model: 使用的模型名称
            result: 查询结果
            ttl: 过期时间(秒)，None 使用配置值

        Returns:
            存储的文档 key
        """
        if not self._initialized or self.redis is None:
            return None

        ttl = ttl or settings.SEMANTIC_CACHE_TTL

        try:
            # 生成向量
            query_vector = get_embedding(query)

            # 规范化 model 字段
            model = model or "qwen"

            # 生成唯一 key
            doc_key = f"{self.PREFIX}{uuid.uuid4().hex}"

            # 序列化结果（处理 date/datetime 等不可 JSON 序列化的类型）
            serialized_result = _serialize_for_json(result)

            # 存储为 Redis JSON
            doc = {
                "query": query,
                "query_vector": query_vector,
                "result": serialized_result,
                "model": model,
                "created_at": time.time(),
                "ttl": ttl,
            }
            await self.redis.json().set(doc_key, "$", doc)

            # 设置 Redis 级别的 TTL（双保险清理）
            await self.redis.expire(doc_key, ttl)

            logger.info(f"SemanticCache: 已存储 (key={doc_key}, ttl={ttl}s)")
            return doc_key

        except Exception as e:
            logger.warning(f"SemanticCache: 存储异常 - {e}")
            return None

    async def close(self):
        """关闭 Redis 连接"""
        if self.redis:
            await self.redis.aclose()
            self.redis = None
            self._initialized = False
            logger.info("SemanticCache: Redis 连接已关闭")


# 全局语义缓存实例
semantic_cache = SemanticCache()
