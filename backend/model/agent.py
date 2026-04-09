from .llm import call_qwen, call_deepseek
from decimal import Decimal
import re

from ..crud.sql_service import execute_sql


def clean_ai_response(text: str) -> str:
    """去除 AI 返回内容中的 Markdown 代码块标记"""
    text = text.strip()
    # 去除开头的 ```json 或 ``` 以及结尾的 ```
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()
def split_tasks(query: str,model:str="qwen"):
    prompt = f"""
    你是数据分析助手，请拆分分析任务：

    问题：{query}

    要求：
    1. 返回JSON数组
    2. 每个元素包含 name 和 query
    3. 不要解释
    4.只输出最重要的2到4个，按重要度排序

    示例：
    [
      {{"name": "平均成绩", "query": "查询各班平均成绩"}},
      {{"name": "人数分布", "query": "统计各班人数"}}
    ]
    """
    if model == "qwen":
        result = call_qwen(prompt)
    elif model == "deepseek":
        result = call_deepseek(prompt)
    else :
        result = call_qwen(prompt)
    import json
    cleaned = clean_ai_response(result)
    print(json.loads(cleaned))
    try:
        return json.loads(cleaned)
    except:
        return []

def generate_sql(query: str,model:str="qwen"):
    prompt = f"""
 你是一个专业的SQL生成助手。请根据用户{query}，生成符合 MySQL 语法的 SQL 查询语句。

## 数据库结构（只允许使用以下表的列名，不要使用不存在的列名，不要臆造列名）

### 表 student
- id (int, 主键, 自增)  # 注意：主键是 id，不是 student_id
- student_no (varchar(50), 唯一, 学生编号)# 注意：这个是学生学号
- name (varchar(50), 学生姓名)
- gender (varchar(10), 性别)
- age (int, 年龄)
- birthplace (varchar(100), 籍贯)
- graduated_school (varchar(100), 毕业院校)
- major (varchar(100), 专业)
- enrollment_date (date, 入学时间)
- graduation_date (date, 毕业时间)
- education (varchar(50), 学历)
- consultant_id (int, 顾问编号)
- class_id (int, 班级ID, 外键关联 class.id)
- is_deleted (tinyint, 默认0, 逻辑删除标记，0=未删除，1=已删除)
- created_at (datetime)
- updated_at (datetime)

### 表 class
- id (int, 主键, 自增)
- class_no (varchar(50), 班级编号)
- class_name (varchar(100), 班级名称)
- start_date (date, 开课时间)
- head_teacher (varchar(50), 班主任)
- course_teacher (varchar(50), 授课老师)
- created_at (datetime)
- updated_at (datetime)

### 表 teacher
- id (int, 主键, 自增)
- teacher_no (varchar(50), 老师编号)
- name (varchar(50), 老师姓名)
- gender (varchar(10), 性别)
- phone (varchar(20), 电话)
- created_at (datetime)
- updated_at (datetime)

### 表 teacher_class (老师带班关系表)
- id (int, 主键, 自增)
- teacher_id (int, 老师ID, 外键关联 teacher.id)
- class_id (int, 班级ID, 外键关联 class.id)

### 表 score
- id (int, 主键, 自增)
- student_id (int, 学生ID, 外键关联 student.id)
- exam_sequence (int, 考核序次)
- score (decimal(5,2), 成绩)
- created_at (datetime)
- updated_at (datetime)

### 表 employment
- id (int, 主键, 自增)
- student_id (int, 学生ID, 外键关联 student.id)
- employment_open_date (date, 就业开放时间)
- offer_date (date, offer下发时间)
- company_name (varchar(100), 就业公司名称)
- salary (int, 薪资, 单位：千元/月)
- created_at (datetime)
- updated_at (datetime)

## 表关系
- student.class_id = class.id
- score.student_id = student.id
- employment.student_id = student.id
- teacher_class.teacher_id = teacher.id
- teacher_class.class_id = class.id

## 生成 SQL 的规则
1. **仅使用上述列名**：禁止使用不存在的列（如 `company_type`）。所有字段必须来自上述表结构。
2. **处理逻辑删除**：查询学生、班级、教师时，默认应添加 `is_deleted = 0` 条件（除非用户明确要求包含已删除记录）。
3. **避免 ONLY_FULL_GROUP_BY 错误**：当使用 `GROUP BY` 时，`SELECT` 中的非聚合列必须全部出现在 `GROUP BY` 中；`ORDER BY` 应使用聚合函数或与 `GROUP BY` 完全相同的表达式，避免使用复杂 `CASE` 语句排序。建议使用列别名排序。
4. **日期格式**：日期比较使用 `DATE()` 函数或直接比较字符串 `'YYYY-MM-DD'`。
5. **聚合查询**：对于统计类问题（如平均分、就业率、薪资分布），请使用适当的聚合函数（`AVG`, `COUNT`, `SUM`, `ROUND` 等），并合理使用 `GROUP BY`。
6. **处理空值**：在计算比率或平均值时，使用 `NULLIF` 避免除零错误，例如 `ROUND(COUNT(e.student_id) * 100.0 / NULLIF(COUNT(s.id), 0), 2)`。
7. **表别名**：为表使用有意义的别名（如 `s` 代表 student，`c` 代表 class），以提高可读性。
8. **输出要求**：只输出 SQL 语句，不要包含额外解释。SQL 语句末尾加分号。

## 示例
用户问题：“统计各专业的学生人数”
SQL：`SELECT major, COUNT(*) AS 学生人数 FROM student WHERE is_deleted = 0 GROUP BY major;`

用户问题：“Java2301 班的平均成绩”
SQL：`SELECT AVG(score) AS 平均分 FROM score s JOIN student stu ON s.student_id = stu.id JOIN class c ON stu.class_id = c.id WHERE c.class_name = 'Java2301' AND stu.is_deleted = 0;`

用户问题：“就业学生的平均薪资”
SQL：`SELECT AVG(salary) AS 平均薪资 FROM employment e JOIN student s ON e.student_id = s.id WHERE s.is_deleted = 0;`

现在，请根据用户的问题生成 SQL。
                  """
    if model=="qwen":
        sql = call_qwen(prompt)
    else:
        sql = call_deepseek(prompt)
    if sql.startswith("ERROR"):
        return sql
    # 简单清洗
    sql = sql.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    # 去除可能的前后引号
    if sql.startswith('"') and sql.endswith('"'):
        sql = sql[1:-1]
    if sql.startswith("'") and sql.endswith("'"):
        sql = sql[1:-1]
    return sql


def generate_analysis(charts,model='qwen'):

    prompt = f"""
    你是数据分析师，请根据以下图表数据生成分析结论：

    {charts}

    要求：
    1. 用中文
    2. 50字到100字
    """
    if model=="qwen":
        return call_qwen(prompt)
    else:
        return call_deepseek(prompt)
import json
def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    else:
        return obj

def ai_choose_chart_type(data: list, title: str, model: str = "qwen") -> str:
    if not data:
        return "bar"

    sample = data[:10]
    sample_serializable = convert_decimal(sample)

    prompt = f"""
你是一个数据分析专家。根据以下查询结果数据，推荐最合适的图表类型。

数据标题: {title}
数据样例（前10行）:
{json.dumps(sample_serializable, ensure_ascii=False, indent=2)}

可选图表类型：
- bar: 柱状图，适合比较不同类别的数值
- line: 折线图，适合展示趋势（如时间序列）
- pie: 饼图，适合展示占比
- scatter: 散点图，适合展示相关性
- area: 面积图，适合累积趋势

请仅输出一个单词，即图表类型（如 bar）。不要输出其他内容。
"""
    if model == "deepseek":
        resp = call_deepseek(prompt)
    else:
        resp = call_qwen(prompt)

    chart_type = resp.strip().lower()
    valid_types = ["bar", "line", "pie", "scatter", "area"]
    return chart_type if chart_type in valid_types else "bar"

def agent_sql(query: str,model:str=""):
    sql = generate_sql(query,model)

    # 如果大模型失败
    if sql.startswith("ERROR"):
        return {"code": 500, "msg": "大模型调用失败", "sql": sql, "data": []}

    # 正确判断
    if not sql.lower().startswith("select"):
        return {"code": 400, "msg": "只允许SELECT查询", "sql": sql, "data": []}

    try:
        data = execute_sql(sql)
        return {"code": 200, "msg": "success", "sql": sql, "data": data}
    except Exception as e:
        return {"code": 500, "msg": str(e), "sql": sql, "data": []}


def dispatch_agent(query: str,model):
    result = agent_sql(query,model)

    return {"code": 200, "action": "sql_query", "result": result}
