"""
飞书自定义机器人 Webhook 推送。

实现目标是轻量卡片推送：生成摘要、精选推荐和原文按钮。
完整飞书应用机器人交互放在 spec 中，不在这里引入 Web 服务框架。
"""

import base64
import hashlib
import hmac
import time
from typing import Optional

import requests

from engine import DigestResult


def _sign(secret: str, timestamp: str) -> str:
    """按飞书自定义机器人签名规则生成签名。"""
    string_to_sign = f"{timestamp}\n{secret}"
    digest = hmac.new(
        string_to_sign.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode("utf-8")


def _trim(text: str, max_len: int = 600) -> str:
    """限制卡片文本长度。"""
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def _fallback_recommendations(digest: DigestResult, limit: int) -> list[dict]:
    """AI 推荐为空时，用热度最高的资讯兜底。"""
    items = sorted(
        list(digest.all_items()),
        key=lambda item: item.score or 0,
        reverse=True,
    )

    recommendations = []
    for item in items[:limit]:
        recommendations.append({
            "title": item.title,
            "source": item.source_display,
            "url": item.url,
            "reason": item.description_cn or item.description,
            "highlight": "热门",
        })

    return recommendations


def build_feishu_card(digest: DigestResult, limit: int = 5) -> dict:
    """构建飞书消息卡片 payload 中的 card 字段。"""
    title = digest.generated_at.strftime("技术日报 %Y-%m-%d")
    summary = "今日技术资讯已整理完成。"
    recommendations = []

    if digest.ai_summary:
        summary = digest.ai_summary.summary or summary
        recommendations = digest.ai_summary.recommendations[:limit]

    if not recommendations:
        recommendations = _fallback_recommendations(digest, limit)

    elements = [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**今日摘要**\n{_trim(summary)}",
            },
        },
        {"tag": "hr"},
    ]

    for index, rec in enumerate(recommendations[:limit], 1):
        title_text = rec.get("title", "未命名")
        source = rec.get("source", "")
        reason = _trim(rec.get("reason", ""), 260)
        highlight = rec.get("highlight", "")
        url = rec.get("url", "")

        label = f"{index}. {title_text}"
        if highlight:
            label = f"{label} · {highlight}"

        content = f"**{label}**"
        if source:
            content += f"\n来源：{source}"
        if reason:
            content += f"\n{reason}"

        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": content,
            },
        })

        if url:
            elements.append({
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "查看原文",
                        },
                        "url": url,
                        "type": "primary",
                    }
                ],
            })

    elements.append({
        "tag": "note",
        "elements": [
            {
                "tag": "plain_text",
                "content": f"共 {digest.total_items} 条内容，由 Tech Digest Daily 自动生成",
            }
        ],
    })

    return {
        "config": {
            "wide_screen_mode": True,
        },
        "header": {
            "template": "blue",
            "title": {
                "tag": "plain_text",
                "content": title,
            },
        },
        "elements": elements,
    }


def build_feishu_payload(
    digest: DigestResult,
    *,
    secret: Optional[str] = None,
    limit: int = 5,
) -> dict:
    """构建飞书自定义机器人 Webhook payload。"""
    payload = {
        "msg_type": "interactive",
        "card": build_feishu_card(digest, limit=limit),
    }

    if secret:
        timestamp = str(int(time.time()))
        payload["timestamp"] = timestamp
        payload["sign"] = _sign(secret, timestamp)

    return payload


def send_digest_feishu(
    digest: DigestResult,
    webhook_url: str,
    *,
    secret: Optional[str] = None,
    limit: int = 5,
    timeout: int = 30,
) -> bool:
    """发送技术日报到飞书自定义机器人。"""
    if not webhook_url:
        raise ValueError("未配置 FEISHU_WEBHOOK_URL")

    payload = build_feishu_payload(digest, secret=secret, limit=limit)
    response = requests.post(webhook_url, json=payload, timeout=timeout)

    if response.status_code != 200:
        print(f"❌ 飞书推送失败: HTTP {response.status_code} {response.text}")
        return False

    data = response.json()
    if data.get("code", 0) == 0:
        print("✅ 飞书推送成功")
        return True

    print(f"❌ 飞书推送失败: {data}")
    return False
