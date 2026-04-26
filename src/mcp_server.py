"""
Tech Digest Daily stdio MCP server。

本文件只做薄包装：MCP tool -> engine.run_digest -> renderer/sender。
stdio 模式下 stdout 只能输出 MCP 协议消息，日志统一写 stderr。
"""

import asyncio
import sys
from contextlib import redirect_stdout
from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Optional

try:
    from mcp.server.fastmcp import FastMCP
    from pydantic import Field
except ImportError as exc:
    print(
        "缺少 MCP 依赖，请先运行: pip install -r requirements-mcp.txt",
        file=sys.stderr,
    )
    raise exc

from core.logger import logger
from engine import DigestResult, get_config, mark_digest_sent, run_digest
from feishu_sender import send_digest_feishu
from renderers import render_json, render_markdown


mcp = FastMCP("tech_digest_mcp")
logger.set_stream(sys.stderr)


class ResponseFormat(str, Enum):
    """日报输出格式。"""

    MARKDOWN = "markdown"
    JSON = "json"


@dataclass
class DigestOptions:
    """MCP 工具内部使用的生成参数。"""

    response_format: ResponseFormat = ResponseFormat.MARKDOWN
    limit: int = 8
    enable_ai: bool = True
    enable_enrich: bool = True
    use_history_dedup: bool = True


def _config_from_options(options: DigestOptions) -> dict:
    """将 MCP 参数合并到环境配置。"""
    config = get_config()
    config["enable_ai_summary"] = options.enable_ai
    config["enable_history_dedup"] = options.use_history_dedup
    return config


def _run_digest_sync(options: DigestOptions) -> DigestResult:
    """同步运行日报生成，确保 stdout 不被日志污染。"""
    config = _config_from_options(options)
    with redirect_stdout(sys.stderr):
        return run_digest(
            config,
            enrich=options.enable_enrich,
            summarize=options.enable_ai,
        )


async def _run_digest(options: DigestOptions) -> DigestResult:
    """在线程中运行同步抓取流程，避免阻塞 MCP 事件循环。"""
    return await asyncio.to_thread(_run_digest_sync, options)


def _format_digest(digest: DigestResult, options: DigestOptions) -> str:
    """按请求格式输出日报。"""
    if options.response_format == ResponseFormat.JSON:
        return render_json(digest, limit=options.limit)
    return render_markdown(digest, limit=options.limit)


def _options(
    response_format: ResponseFormat,
    limit: int,
    enable_ai: bool,
    enable_enrich: bool,
    use_history_dedup: bool,
) -> DigestOptions:
    """构造并兜底修正 MCP 参数。"""
    return DigestOptions(
        response_format=response_format,
        limit=max(1, min(limit, 50)),
        enable_ai=enable_ai,
        enable_enrich=enable_enrich,
        use_history_dedup=use_history_dedup,
    )


@mcp.tool(
    name="tech_digest_get_daily_digest",
    annotations={
        "title": "Get Tech Digest Daily",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def tech_digest_get_daily_digest(
    response_format: Annotated[
        ResponseFormat,
        Field(description="输出格式：markdown 适合聊天窗口，json 适合程序处理。"),
    ] = ResponseFormat.MARKDOWN,
    limit: Annotated[int, Field(ge=1, le=50, description="返回的最大资讯条数。")] = 8,
    enable_ai: Annotated[bool, Field(description="是否启用 AI 总结。")] = True,
    enable_enrich: Annotated[bool, Field(description="是否抓取 GitHub README 等深度信息。")] = True,
    use_history_dedup: Annotated[bool, Field(description="是否启用历史去重。")] = True,
) -> str:
    """生成今日技术日报。

    Args:
        response_format: 输出格式，支持 markdown 或 json。
        limit: 返回的最大资讯条数，范围 1-50。
        enable_ai: 是否启用 AI 总结。
        enable_enrich: 是否抓取 GitHub README 等深度信息。
        use_history_dedup: 是否启用历史去重。

    Returns:
        str: Markdown 或 JSON 字符串。Markdown 适合直接回复用户，JSON 适合后续程序处理。
    """
    try:
        options = _options(response_format, limit, enable_ai, enable_enrich, use_history_dedup)
        digest = await _run_digest(options)
        return _format_digest(digest, options)
    except Exception as e:
        return f"Error: 生成技术日报失败: {e}. 请检查网络、API Key 和数据源配置。"


@mcp.tool(
    name="tech_digest_get_recommendations",
    annotations={
        "title": "Get Tech Digest Recommendations",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def tech_digest_get_recommendations(
    limit: Annotated[int, Field(ge=1, le=20, description="返回的最大推荐条数。")] = 5,
    enable_ai: Annotated[bool, Field(description="是否启用 AI 总结。")] = True,
    enable_enrich: Annotated[bool, Field(description="是否抓取 GitHub README 等深度信息。")] = True,
    use_history_dedup: Annotated[bool, Field(description="是否启用历史去重。")] = True,
) -> str:
    """生成今日技术日报，并只返回精选推荐。

    Args:
        limit: 返回的最大推荐条数。
        enable_ai: 是否启用 AI 总结，建议保持 true。
        enable_enrich: 是否抓取深度信息。
        use_history_dedup: 是否启用历史去重。

    Returns:
        str: Markdown 格式的精选推荐列表。
    """
    try:
        options = _options(
            ResponseFormat.MARKDOWN,
            limit,
            enable_ai,
            enable_enrich,
            use_history_dedup,
        )
        digest = await _run_digest(options)
        markdown = render_markdown(digest, limit=options.limit)
        marker = "## 精选推荐"
        if marker not in markdown:
            return "今日没有生成 AI 推荐，可调用 tech_digest_get_daily_digest 查看完整日报。"
        return markdown[markdown.index(marker):]
    except Exception as e:
        return f"Error: 生成精选推荐失败: {e}. 请检查 LLM_API_KEY 或关闭 enable_ai。"


@mcp.tool(
    name="tech_digest_send_feishu",
    annotations={
        "title": "Send Tech Digest To Feishu",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def tech_digest_send_feishu(
    limit: Annotated[int, Field(ge=1, le=20, description="飞书卡片展示的最大条数。")] = 5,
    enable_ai: Annotated[bool, Field(description="是否启用 AI 总结。")] = True,
    enable_enrich: Annotated[bool, Field(description="是否抓取 GitHub README 等深度信息。")] = True,
    use_history_dedup: Annotated[bool, Field(description="是否启用历史去重。")] = True,
    webhook_url: Annotated[
        Optional[str],
        Field(description="飞书自定义机器人 Webhook URL；为空时读取 FEISHU_WEBHOOK_URL。"),
    ] = None,
    secret: Annotated[
        Optional[str],
        Field(description="飞书自定义机器人签名密钥；为空时读取 FEISHU_SECRET。"),
    ] = None,
) -> str:
    """生成技术日报并发送到飞书自定义机器人。

    Args:
        limit: 飞书卡片展示的最大条数。
        enable_ai: 是否启用 AI 总结。
        enable_enrich: 是否抓取深度信息。
        use_history_dedup: 是否启用历史去重。
        webhook_url: 飞书自定义机器人 Webhook URL。
        secret: 飞书自定义机器人签名密钥。

    Returns:
        str: 发送结果说明。发送成功后会写入历史去重记录。
    """
    try:
        options = _options(
            ResponseFormat.MARKDOWN,
            limit,
            enable_ai,
            enable_enrich,
            use_history_dedup,
        )
        digest = await _run_digest(options)
        if not digest.has_items:
            return "去重后无新内容，已跳过飞书推送。"

        config = _config_from_options(options)
        target_webhook_url = webhook_url or config["feishu_webhook_url"]
        target_secret = secret or config["feishu_secret"]
        if not target_webhook_url:
            return "Error: 未配置 FEISHU_WEBHOOK_URL，也没有传入 webhook_url。"

        with redirect_stdout(sys.stderr):
            success = send_digest_feishu(
                digest,
                target_webhook_url,
                secret=target_secret,
                limit=options.limit,
            )

        if not success:
            return "Error: 飞书推送失败，请检查 webhook、签名密钥和机器人权限。"

        mark_digest_sent(digest)
        return f"已发送 {min(options.limit, digest.total_items)} 条技术日报到飞书。"
    except Exception as e:
        return f"Error: 飞书推送流程失败: {e}. 请检查网络、webhook 和密钥配置。"


if __name__ == "__main__":
    mcp.run(transport="stdio")
