import requests

from backend.core.config import QWEN_API_KEY, QWEN_URL, DEEPSEEK_API_KEY, DEEPSEEK_URL


def call_qwen(prompt: str):
    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "qwen-plus",
        "input": {
            "messages": [
                {"role": "system", "content": "你是SQL生成助手"},
                {"role": "system", "content":
                    "数据库表：student(学生表)，class(班级表)，teacher(教师表)，teacher_class (老师带班关系表)，score(学生成绩表)，employment(就业情况表)"
                    "注意各个表之间的外键关系"
                    ""},
                {"role": "user", "content": prompt},
            ]
        },
    }

    resp = requests.post(QWEN_URL, json=data, headers=headers)
    result = resp.json()
    print("千问返回：", result)
    try:
        # 新版（chat格式）
        if "choices" in result.get("output", {}):
            return result["output"]["choices"][0]["message"]["content"]
        # 旧版（text格式）
        if "text" in result.get("output", {}):
            return result["output"]["text"]
        return f"ERROR: 未知返回格式 {result}"
    except Exception as e:
        return f"ERROR: {result}"

def call_deepseek(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "deepseek-chat",   # 或其他模型名
        "messages": [
            {"role": "system", "content": "你是数据分析和 SQL 生成助手，根据用户问题返回 JSON 格式的图表数据和分析结论。"},
            {"role": "system", "content":
                "数据库表：student(学生表)，class(班级表)，teacher(教师表)，teacher_class (老师带班关系表)，score(学生成绩表)，employment(就业情况表)"
                "注意各个表之间的外键关系以及逻辑删除功能"
                "生成sql语句时只返回sql语句，不要返回其他东西,"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
    }
    resp = requests.post(DEEPSEEK_URL, json=data, headers=headers)
    result = resp.json()
    print("deepseek返回", result)
    try:
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"ERROR: DeepSeek 调用失败 - {result}"