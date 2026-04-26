"""JSON 输出渲染器。"""

import json
from datetime import datetime
from typing import Optional

from engine import DigestResult


def _json_default(value):
    """处理 JSON 不直接支持的对象。"""
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"{type(value).__name__} is not JSON serializable")


def _summary_to_dict(digest: DigestResult) -> Optional[dict]:
    """将 AI 总结转换为字典。"""
    if not digest.ai_summary:
        return None

    return {
        "summary": digest.ai_summary.summary,
        "recommendations": digest.ai_summary.recommendations,
        "generated_at": digest.ai_summary.generated_at,
    }


def render_json(digest: DigestResult, limit: Optional[int] = None, indent: int = 2) -> str:
    """将日报结果渲染为 JSON 字符串。"""
    items = list(digest.all_items())
    if limit:
        items = items[:limit]

    payload = {
        "generated_at": digest.generated_at,
        "total_items": digest.total_items,
        "returned_items": len(items),
        "ai_summary": _summary_to_dict(digest),
        "sources": [
            {
                "source": result.source.value,
                "success": result.success,
                "count": result.count,
                "error_message": result.error_message,
            }
            for result in digest.results
        ],
        "items": [item.to_dict() for item in items],
    }

    return json.dumps(payload, ensure_ascii=False, indent=indent, default=_json_default)
