from backend.crud.sql_service import execute_sql
from backend.model.agent import split_tasks, generate_sql, ai_choose_chart_type


def choose_chart_type(data):
    if not data:
        return "none"

    keys = list(data[0].keys())

    if len(keys) == 2:
        # 分类 + 数值
        return "bar"

    if "time" in keys[0].lower():
        return "line"

    return "table"


def build_bar_option(data):
    x = [item[list(item.keys())[0]] for item in data]
    y = [item[list(item.keys())[1]] for item in data]

    return {
        "xAxis": {"type": "category", "data": x},
        "yAxis": {"type": "value"},
        "series": [{"type": "bar", "data": y}],
    }


def build_line_option(data):
    x = [item[list(item.keys())[0]] for item in data]
    y = [item[list(item.keys())[1]] for item in data]

    return {
        "xAxis": {"type": "category", "data": x},
        "yAxis": {"type": "value"},
        "series": [{"type": "line", "data": y}],
    }


def build_pie_option(data):
    return {
        "series": [
            {
                "type": "pie",
                "data": [
                    {"name": list(d.values())[0], "value": list(d.values())[1]}
                    for d in data
                ],
            }
        ]
    }


# def build_option(title, data):
#     if not data:
#         return {}
#
#     keys = list(data[0].keys())
#
#     x_key = keys[0]
#
#     # 自动找数值列
#     y_keys = []
#     for k in keys[1:]:
#         if isinstance(data[0][k], (int, float)):
#             y_keys.append(k)
#
#     # 如果没有数值列，直接返回空
#     if not y_keys:
#         return {}
#
#     x_data = [row[x_key] for row in data]
#
#     series = []
#     for y_key in y_keys:
#         series.append(
#             {"name": y_key, "type": "bar", "data": [row[y_key] for row in data]}
#         )
#
#     return {
#         "title": {"text": title},
#         "tooltip": {"trigger": "axis"},
#         "legend": {"data": y_keys},
#         "xAxis": {"type": "category", "data": x_data},
#         "yAxis": {"type": "value"},
#         "series": series,
#     }
def build_option(title, data, chart_type="bar"):
    if not data:
        return {}

    keys = list(data[0].keys())
    if len(keys) < 2:
        return {}

    x_key = keys[0]
    y_key = keys[1]

    x_data = [str(row[x_key]) for row in data]
    y_data = [row[y_key] for row in data]

    # 基础配置
    option = {
        "title": {"text": title},
        "tooltip": {"trigger": "axis"},
    }

    # 根据图表类型生成不同配置
    if chart_type == "pie":
        # 饼图需要 {name, value} 格式
        pie_data = [{"name": name, "value": value} for name, value in zip(x_data, y_data)]
        option["series"] = {"type": "pie", "data": pie_data, "radius": "50%"}
        option["tooltip"]["trigger"] = "item"
        # 饼图不需要 xAxis 和 yAxis
    else:
        option["xAxis"] = {"type": "category", "data": x_data}
        option["yAxis"] = {"type": "value", "name": y_key}
        if chart_type == "line":
            option["series"] = {"type": "line", "data": y_data, "name": y_key}
        elif chart_type == "area":
            option["series"] = {"type": "line", "data": y_data, "name": y_key, "areaStyle": {}}
        elif chart_type == "scatter":
            # 散点图数据格式: [[x, y], ...]
            scatter_data = [[i, v] for i, v in enumerate(y_data)]
            option["series"] = {"type": "scatter", "data": scatter_data, "name": y_key}
        else:  # 默认 bar
            option["series"] = {"type": "bar", "data": y_data, "name": y_key}

    return option


def build_chart(data: list, title: str, chart_type: str = "bar") -> dict:
    if not data:
        return {"title": {"text": title}, "tooltip": {}}

    # 获取列名（假设第一列为 x 轴类别，第二列为数值）
    columns = list(data[0].keys())
    x_axis = [str(row[columns[0]]) for row in data]
    y_series = []
    for row in data:
        val = row[columns[1]]
        try:
            y_series.append(float(val))
        except (ValueError, TypeError):
            y_series.append(0)

    # 基础配置
    option = {
        "title": {"text": title},
        "tooltip": {"trigger": "axis"},
    }
    # print(chart_type)
    # 根据图表类型生成不同配置
    if chart_type == "pie":
        pie_data = [{"name": name, "value": value} for name, value in zip(x_axis, y_series)]
        option["series"] = {"type": "pie", "data": pie_data, "radius": "50%"}
        option["tooltip"]["trigger"] = "item"
        # 饼图不需要 xAxis 和 yAxis
    else:
        option["xAxis"] = {"type": "category", "data": x_axis}
        option["yAxis"] = {"type": "value", "name": columns[1]}
        if chart_type == "line":
            option["series"] = {"type": "line", "data": y_series, "name": columns[1]}
        elif chart_type == "area":
            option["series"] = {"type": "line", "data": y_series, "name": columns[1], "areaStyle": {}}
        elif chart_type == "scatter":
            # 散点图数据格式: [[x, y], ...]
            scatter_data = [[i, v] for i, v in enumerate(y_series)]
            option["series"] = {"type": "scatter", "data": scatter_data, "name": columns[1]}
        else:  # 默认 bar
            option["series"] = {"type": "bar", "data": y_series, "name": columns[1]}

    return option
def build_dashboard(query: str,model:str="qwen"):
    #拆分任务为2-4个分任务
    tasks = split_tasks(query,model)

    charts = []

    for task in tasks:
        try:
            # 循环分任务生成SQL
            sql = generate_sql(task["query"],model)
            print(sql)
            if sql.startswith("ERROR"):
                continue

            # 执行SQL
            data = execute_sql(sql)
            # print(data)
            if not data:
                print(f"SQL执行无数据: {sql}")
                continue
            chart_type = ai_choose_chart_type(data, task["name"], model)
            # 生成图表
            option = build_chart(data, task["name"], chart_type)

            charts.append({
                "title": task["name"],
                "sql": sql,
                "option": option,
                "chart_type": chart_type  # 可选，调试用
            })
        except Exception as e:
            # 记录错误并继续下一个任务
            print(f"处理任务 '{task['name']}' 时出错: {e}")
            continue
    return charts
