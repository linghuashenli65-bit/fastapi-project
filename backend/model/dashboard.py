from backend.crud.sql_service import execute_sql, convert_decimal
from backend.model.agent import split_tasks, generate_sql, ai_choose_chart_type, agent_sql, generate_analysis


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
async def build_dashboard(query: str,model:str="qwen",analysis_length: str = "medium"):
    #拆分任务为2-4个分任务
    tasks = await split_tasks(query,model)
    if not isinstance(tasks, list):
        yield {"stage": "error", "message": f"任务分解失败，返回了 {type(tasks)} 类型的数据"}
        return
    if not tasks:
        yield {"stage": "error", "message": "没有有效的分析任务"}
        return
    yield {"stage": "split", "percent": 10, "message": f"分解为 {len(tasks)} 个任务"}
    charts = []
    total = len(tasks)
    for idx, task in enumerate(tasks):
        try:
            # 循环分任务生成SQL
            yield {"stage": "sql", "percent": 10 + (idx / total) * 30, "message": f"生成 SQL：{task['name']}"}
            sql = await generate_sql(task["query"], model)
            if sql.startswith("ERROR"):
                continue

            # 执行SQL
            yield {"stage": "execute", "percent": 40 + (idx / total) * 30, "message": f"执行 SQL：{task['name']}"}
            data =await execute_sql(sql)
            # print(data)
            if not data:
                print(f"SQL执行无数据: {sql}")
                continue
            #推荐图表类型
            yield {"stage": "chart_type", "percent": 70 + (idx / total) * 20, "message": f"选择图表类型：{task['name']}"}
            chart_type =await ai_choose_chart_type(data, task["name"], model)
            # 生成图表
            option = build_chart(data, task["name"], chart_type)

            charts.append({
                "title": task["name"],
                "option": option,
                "table": {"columns": list(data[0].keys()), "rows": data[:20]}
            })
        except Exception as e:
            # 记录错误并继续下一个任务
            print(f"处理任务 '{task['name']}' 时出错: {e}")
            continue
    charts = convert_decimal(charts)
    yield {"stage": "complete", "percent": 100, "message": "正在生成图表总结", "charts": charts}
    # 在所有任务完成后，生成分析结论
    analysis =await generate_analysis(charts, model,analysis_length)  # 需要传入 model 参数
    yield {"stage": "complete", "percent": 100, "message": "分析完成", "analysis": analysis}
