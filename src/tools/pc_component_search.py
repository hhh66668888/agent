"""电脑硬件价格联网搜索工具"""

from langchain.tools import tool
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def search_pc_component(component_name: str, color: str = "") -> str:
    """搜索电脑硬件的具体型号和实时价格。

    Args:
        component_name: 硬件类别名称，如 "CPU"、"显卡"、"主板"、"内存"、"固态硬盘"、"散热器"、"电源"、"机箱"、"机箱风扇" 等。
        color: 颜色偏好，如 "白色" 或 "黑色"，留空表示不限颜色。
    """
    ctx = request_context.get() or new_context(method="search_pc_component")
    client = SearchClient(ctx=ctx)

    color_str = f" {color}" if color else ""
    query = f"{component_name}{color_str} 价格 2025"
    # 优先从京东搜索价格，确保价格准确性
    response = client.search(
        query=query,
        search_type="web",
        count=8,
        sites="jd.com"
    )

    # 如果京东搜索结果不足，补充全网搜索
    if not response.web_items or len(response.web_items) < 3:
        response_extra = client.web_search(query=f"{component_name}{color_str} 京东价格 2025", count=5)
        if response_extra.web_items:
            combined_items = list(response.web_items or []) + list(response_extra.web_items)
            response.web_items = combined_items

    if not response.web_items:
        return f"未找到{color_str} {component_name} 的相关价格信息"

    results = []
    for item in response.web_items[:8]:
        title = item.title or ""
        snippet = item.snippet or ""
        results.append(f"[{title}] {snippet}")

    return f"\n---\n".join(results)


@tool
def search_pc_build_config(budget: str, usage: str, color: str = "", aesthetic: str = "") -> str:
    """根据预算、用途、颜色等需求搜索整机配置方案参考。

    Args:
        budget: 预算金额，如 "5000元"、"10000元"。
        usage: 主要用途，如 "打游戏"、"办公"、"剪辑视频"、"3A大作"。
        color: 颜色偏好，如 "白色" 或 "黑色"。
        aesthetic: 是否需要颜值/灯效，如 "要颜值好看"、"不需要颜值"。
    """
    ctx = request_context.get() or new_context(method="search_pc_build_config")
    client = SearchClient(ctx=ctx)

    aesthetic_str = f" {aesthetic}" if aesthetic else ""
    color_str = f" {color}" if color else ""
    query = f"2025年{budget}电脑配置推荐{color_str}{aesthetic_str} {usage} 装机清单 京东价格"
    # 优先从京东搜索配置方案和价格
    response = client.search(
        query=query,
        search_type="web",
        count=10,
        sites="jd.com",
        need_summary=True
    )

    # 如果京东结果不足，补充全网搜索
    if not response.web_items or len(response.web_items) < 3:
        response_extra = client.web_search_with_summary(
            query=f"2025年{budget}电脑配置推荐{color_str}{aesthetic_str} {usage} 京东价格",
            count=5
        )
        if response_extra.web_items:
            combined_items = list(response.web_items or []) + list(response_extra.web_items)
            response.web_items = combined_items
        if not response.summary and response_extra.summary:
            response.summary = response_extra.summary

    output_parts = []
    if response.summary:
        output_parts.append(f"【AI摘要】{response.summary}")

    if response.web_items:
        for item in response.web_items[:10]:
            title = item.title or ""
            snippet = item.snippet or ""
            output_parts.append(f"[{title}] {snippet}")

    if not output_parts:
        return f"未找到预算{budget}、用途{usage}的配置方案"

    return "\n---\n".join(output_parts)
