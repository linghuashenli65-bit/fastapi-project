"""
下载 Embedding 模型到本地
使用方法: python -m backend.utils.download_model
"""
from sentence_transformers import SentenceTransformer
import os

# 模型名称
MODEL_NAME = "shibing624/text2vec-base-chinese"
# 本地保存路径（项目根目录下的 models 文件夹）
LOCAL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models", "text2vec-base-chinese")

def main():
    print(f"正在下载模型: {MODEL_NAME}")
    print(f"保存到: {LOCAL_PATH}")
    
    # 自动下载并保存到本地
    model = SentenceTransformer(MODEL_NAME)
    model.save(LOCAL_PATH)
    
    print(f"模型下载完成！")
    print(f"本地路径: {LOCAL_PATH}")

if __name__ == "__main__":
    main()
