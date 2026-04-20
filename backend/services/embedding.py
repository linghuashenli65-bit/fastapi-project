"""
Embedding 服务：使用本地 sentence-transformers 模型生成文本向量
"""
import numpy as np
from sentence_transformers import SentenceTransformer

from backend.core.config import settings
from backend.core.logger import get_logger

logger = get_logger("embedding")

# 全局模型实例（懒加载）
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """懒加载 Embedding 模型"""
    global _model
    if _model is None:
        model_name = settings.EMBEDDING_MODEL_NAME
        logger.info(f"正在加载 Embedding 模型: {model_name}")
        _model = SentenceTransformer(model_name)
        logger.info(f"Embedding 模型加载完成, 向量维度: {_model.get_embedding_dimension()}")
    return _model


def get_embedding(text: str) -> list[float]:
    """
    生成文本的向量表示

    Args:
        text: 输入文本

    Returns:
        向量列表 (float32)
    """
    model = _get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.astype(np.float32).tolist()


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    批量生成文本向量

    Args:
        texts: 输入文本列表

    Returns:
        向量列表
    """
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True)
    return vectors.astype(np.float32).tolist()


def get_embedding_dim() -> int:
    """获取当前模型的向量维度"""
    model = _get_model()
    return model.get_embedding_dimension()
