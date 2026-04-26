"""Markdown 输出渲染器。"""

from collections import defaultdict
from typing import Optional

from engine import DigestResult
from models import ContentType, NewsItem, SOURCE_DISPLAY


CONTENT_TITLES = {
    ContentType.PROJECT: "开源项目",
    ContentType.ARTICLE: "技术文章",
    ContentType.PRODUCT: "新品发布",
}


def _trim(text: str, max_len: int = 180) -> str:
    """限制文本长度，避免聊天窗口被单条内容撑满。"""
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def _item_meta(item: NewsItem) -> str:
    """生成一行紧凑元信息。"""
    parts = [SOURCE_DISPLAY.get(item.source, item.source.value)]
    if item.score:
        parts.append(f"热度 {item.score}")
    if item.comments:
        parts.append(f"评论 {item.comments}")
    if item.author:
        parts.append(f"作者 {item.author}")

    language = item.extra.get("language")
    if language:
        parts.append(language)

    return " · ".join(parts)


def _render_recommendations(digest: DigestResult, limit: int) -> list[str]:
    """渲染 AI 推荐区。"""
    if not digest.ai_summary or not digest.ai_summary.recommendations:
        return []

    lines = ["## 精选推荐", ""]
    for index, rec in enumerate(digest.ai_summary.recommendations[:limit], 1):
        title = rec.get("title", "未命名")
        url = rec.get("url", "")
        source = rec.get("source", "")
        highlight = rec.get("highlight", "")
        reason = _trim(rec.get("reason", ""), 240)

        title_text = f"[{title}]({url})" if url else title
        badge = f" {highlight}" if highlight else ""
        lines.append(f"{index}. **{title_text}**{badge}")
        if source:
            lines.append(f"   - 来源：{source}")
        if reason:
            lines.append(f"   - 推荐理由：{reason}")
        lines.append("")

    return lines


def _render_items(digest: DigestResult, limit: int) -> list[str]:
    """按内容类型渲染资讯列表。"""
    grouped = defaultdict(list)
    for item in digest.all_items():
        grouped[item.content_type].append(item)

    lines = []
    remaining = limit
    for content_type in [ContentType.PROJECT, ContentType.ARTICLE, ContentType.PRODUCT]:
        items = grouped.get(content_type, [])
        if not items or remaining <= 0:
            continue

        lines.extend([f"## {CONTENT_TITLES.get(content_type, '内容')}", ""])
        for item in items[:remaining]:
            title = f"[{item.title}]({item.url})" if item.url else item.title
            desc = _trim(item.description_cn or item.description)
            lines.append(f"- **{title}**")
            if desc:
                lines.append(f"  {desc}")
            lines.append(f"  `{_item_meta(item)}`")
            lines.append("")

        remaining -= len(items[:remaining])

    return lines


def render_markdown(digest: DigestResult, limit: Optional[int] = None) -> str:
    """将日报结果渲染为适合 CLI、MCP、聊天窗口的 Markdown。"""
    item_limit = limit or digest.total_items
    rec_limit = min(5, item_limit)
    date_text = digest.generated_at.strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# 技术日报 {date_text}",
        "",
        f"今日精选 {digest.total_items} 条内容。",
        "",
    ]

    if digest.ai_summary and digest.ai_summary.summary:
        lines.extend(["## 今日总结", "", digest.ai_summary.summary.strip(), ""])

    lines.extend(_render_recommendations(digest, rec_limit))
    lines.extend(_render_items(digest, item_limit))

    return "\n".join(lines).strip() + "\n"
