# backend/utils/helpers.py
import re

def clean_ai_response(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    # 去除开头的 ``` 及可选的 language（如 json, sql），以及结尾的 ```
    text = re.sub(r'^```(?:[a-zA-Z0-9_]*)?\s*\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\n?```$', '', text)
    return text.strip()