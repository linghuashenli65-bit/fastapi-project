from .agent import split_tasks, generate_sql, ai_choose_chart_type, generate_analysis
from .llm import call_qwen, call_deepseek
from backend.repositories.sql_service import execute_sql
from backend.utils.helpers import ai_two_level_cache
from decimal import Decimal
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


async def build_dashboard(query: str, model: str = "qwen", analysis_length: str = "medium"):
    # 尝试从缓存获取完整结果
    cached_result = await _get_dashboard_cache(query, model, analysis_length)
    if cached_result is not None:
        # 缓存命中：快速推送进度 + 直接返回完整结果
        yield {"stage": "cache_hit", "percent": 0, "message": "检测到相似查询，正在加载缓存结果..."}
        yield {"stage": "cache_hit", "percent": 50, "message": "加载缓存中..."}
        yield {
            "stage": "complete", "percent": 100, "message": "分析完成（缓存命中）",
            "analysis": cached_result.get("analysis", ""),
            "charts": cached_result.get("charts", [])
        }
        return

    # 1. 任务分解 (0% -> 10%)
    yield {"stage": "split", "percent": 0, "message": "正在分析问题并分解任务..."}
    tasks = await split_tasks(query, model)
    if not isinstance(tasks, list):
        yield {"stage": "error", "message": f"任务分解失败，返回了 {type(tasks)} 类型的数据"}
        return
    if not tasks:
        yield {"stage": "error", "message": "没有有效的分析任务"}
        return
    yield {"stage": "split", "percent": 10, "message": f"分解为 {len(tasks)} 个任务"}

    total = len(tasks)
    charts = []

    # 每个任务占用的进度区间 (10% -> 70%，共 60%)
    task_progress_range = 60.0
    base_progress = 10.0

    for idx, task in enumerate(tasks):
        # 计算当前任务的起始和结束进度
        task_start = base_progress + (idx / total) * task_progress_range
        task_end = base_progress + ((idx + 1) / total) * task_progress_range
        # 任务内部分为：生成SQL(20%)、执行SQL(30%)、选择图表类型(20%)、构建图表(30%)
        sub_stages = [0.2, 0.3, 0.2, 0.3]  # 子阶段权重

        try:
            # 生成 SQL（重试机制）
            max_retries = 3
            sql = None
            data = None
            error_msg = ""

            for attempt in range(max_retries + 1):
                try:
                    # 更新消息：生成SQL
                    sub_progress = task_start + sub_stages[0] * (task_end - task_start)
                    if attempt == 0:
                        yield {
                            "stage": "sql_generate",
                            "percent": round(sub_progress, 1),
                            "message": f"正在为任务「{task['name']}」生成SQL语句"
                        }
                        sql = await generate_sql(task["query"], model)
                    else:
                        sub_progress = task_start + (sub_stages[0] + 0.1) * (task_end - task_start)  # 重试略微前进
                        yield {
                            "stage": "sql_retry",
                            "percent": round(sub_progress, 1),
                            "message": f"SQL生成失败，正在重试（第 {attempt} 次）..."
                        }
                        sql = await generate_sql(task["query"], model, error_feedback=error_msg)

                    # 执行 SQL
                    sub_progress = task_start + (sub_stages[0] + sub_stages[1]) * (task_end - task_start)
                    yield {
                        "stage": "sql_execute",
                        "percent": round(sub_progress, 1),
                        "message": f"正在执行SQL：{task['name']}"
                    }
                    data = await execute_sql(sql)
                    break  # 成功则跳出重试循环

                except Exception as e:
                    error_msg = str(e)
                    print(f"任务 '{task['name']}' 失败 (尝试 {attempt + 1}/{max_retries + 1}): {error_msg}")
                    if attempt == max_retries:
                        data = None
                        break

            if not data:
                yield {
                    "stage": "error",
                    "percent": round(task_end, 1),
                    "message": f"任务 '{task['name']}' 执行失败，跳过该任务"
                }
                continue

            # 选择图表类型
            sub_progress = task_start + (sub_stages[0] + sub_stages[1] + sub_stages[2]) * (task_end - task_start)
            yield {
                "stage": "chart_type",
                "percent": round(sub_progress, 1),
                "message": f"正在为「{task['name']}」选择最佳图表类型"
            }
            chart_type = await ai_choose_chart_type(data, task["name"], model)

            # 构建图表
            sub_progress = task_end  # 最后一个子阶段结束正好到达 task_end
            yield {
                "stage": "build_chart",
                "percent": round(sub_progress, 1),
                "message": f"正在生成图表：{task['name']}"
            }
            option = build_chart(data, task["name"], chart_type)

            charts.append({
                "title": task["name"],
                "option": option,
                "table": {"columns": list(data[0].keys()), "rows": data[:20]}
            })

        except Exception as e:
            print(f"处理任务 '{task['name']}' 时出错: {e}")
            yield {
                "stage": "error",
                "percent": round(task_end, 1),
                "message": f"任务「{task['name']}」处理失败：{str(e)}"
            }
            continue

    # 2. 图表后处理 (70% -> 85%)
    yield {"stage": "postprocess", "percent": 70, "message": "正在整理图表数据..."}
    charts = convert_decimal(charts)
    yield {"stage": "postprocess", "percent": 85, "message": f"共生成 {len(charts)} 个图表"}

    # 3. 生成分析结论 (85% -> 100%)
    yield {"stage": "analysis", "percent": 85, "message": "正在生成综合分析报告..."}
    analysis = await generate_analysis(charts, model, analysis_length)

    # 写入语义缓存
    await _set_dashboard_cache(query, model, analysis_length, {
        "analysis": analysis,
        "charts": charts
    })

    yield {"stage": "complete", "percent": 100, "message": "分析完成", "analysis": analysis, "charts": charts}


async def _get_dashboard_cache(query: str, model: str, analysis_length: str) -> dict | None:
    """从语义缓存获取 dashboard 结果"""
    try:
        from backend.services.semantic_cache import semantic_cache
        if not semantic_cache._initialized:
            return None
        # 将 analysis_length 纳入查询上下文
        cache_query = f"[dashboard:{analysis_length}] {query}"
        return await semantic_cache.search(cache_query)
    except Exception:
        return None


async def _set_dashboard_cache(query: str, model: str, analysis_length: str, result: dict):
    """将 dashboard 结果写入语义缓存"""
    try:
        from backend.services.semantic_cache import semantic_cache
        if not semantic_cache._initialized:
            return
        cache_query = f"[dashboard:{analysis_length}] {query}"
        await semantic_cache.store(cache_query, model, result)
    except Exception:
        pass
