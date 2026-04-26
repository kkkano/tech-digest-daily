"""
技术日报生成引擎。

这里保留原 main.py 的主干流程：抓取、去重、深度补充、AI 总结。
发送邮件、推送飞书、CLI 输出、MCP 调用都只消费 DigestResult。
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from ai.summarizer import generate_ai_summary
from core.logger import logger
from dedup.history import HistoryDedup
from dedup.memory import MemoryDedup
from models import AISummary, SourceResult
from sources.depth_fetcher import enrich_results
from sources.devto import DevToSource
from sources.github_trending import GitHubTrendingSource
from sources.hackernews import HackerNewsSource
from sources.producthunt import ProductHuntSource


@dataclass
class DigestResult:
    """一次技术日报生成结果。"""

    results: list[SourceResult]
    ai_summary: Optional[AISummary]
    generated_at: datetime = field(default_factory=datetime.now)
    total_items: int = 0
    history_dedup: Optional[Any] = field(default=None, repr=False)

    @property
    def has_items(self) -> bool:
        """是否包含可发送内容。"""
        return self.total_items > 0

    def all_items(self):
        """按数据源顺序展开全部资讯项。"""
        for result in self.results:
            if result.success:
                yield from result.items


def _env_bool(name: str, default: bool = True) -> bool:
    """读取布尔环境变量。"""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.lower() == "true"


def _env_int(name: str, default: int) -> int:
    """读取整型环境变量。"""
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        logger.warning(f"{name} 不是合法整数，使用默认值 {default}")
        return default


def get_config() -> dict:
    """获取运行配置。"""
    return {
        "to_email": os.environ.get("TO_EMAIL"),
        "github_username": os.environ.get("GITHUB_USERNAME", ""),
        "llm_api_key": os.environ.get("LLM_API_KEY"),
        "github_token": os.environ.get("GITHUB_TOKEN"),
        "feishu_webhook_url": os.environ.get("FEISHU_WEBHOOK_URL"),
        "feishu_secret": os.environ.get("FEISHU_SECRET"),

        # 数据源开关
        "enable_github": _env_bool("ENABLE_GITHUB", True),
        "enable_hackernews": _env_bool("ENABLE_HACKERNEWS", True),
        "enable_producthunt": _env_bool("ENABLE_PRODUCTHUNT", True),
        "enable_devto": _env_bool("ENABLE_DEVTO", True),

        # 数量配置
        "github_limit": _env_int("GITHUB_LIMIT", 15),
        "hackernews_limit": _env_int("HACKERNEWS_LIMIT", 10),
        "producthunt_limit": _env_int("PRODUCTHUNT_LIMIT", 8),
        "devto_limit": _env_int("DEVTO_LIMIT", 10),

        # AI 总结开关
        "enable_ai_summary": _env_bool("ENABLE_AI_SUMMARY", True),

        # 历史去重开关
        "enable_history_dedup": _env_bool("ENABLE_HISTORY_DEDUP", True),
    }


def fetch_all_sources(config: dict) -> list[SourceResult]:
    """并发获取所有启用的数据源。"""
    results = []
    sources = []

    if config["enable_github"]:
        sources.append(("GitHub Trending", GitHubTrendingSource(), config["github_limit"]))
    if config["enable_hackernews"]:
        sources.append(("Hacker News", HackerNewsSource(), config["hackernews_limit"]))
    if config["enable_producthunt"]:
        sources.append(("Product Hunt", ProductHuntSource(), config["producthunt_limit"]))
    if config["enable_devto"]:
        sources.append(("Dev.to", DevToSource(), config["devto_limit"]))

    logger.section(f"📡 正在获取 {len(sources)} 个数据源...")

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(source.fetch, limit): name
            for name, source, limit in sources
        }

        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                results.append(result)
                logger.source_result(
                    name,
                    result.success,
                    result.count if result.success else 0,
                )
            except Exception as e:
                logger.source_result(name, False, error=str(e))

    return results


def apply_dedup(results: list[SourceResult], config: dict):
    """应用内存去重和历史去重。"""
    memory_dedup = MemoryDedup()

    history_dedup = None
    if config["enable_history_dedup"]:
        history_dedup = HistoryDedup()

    deduped_results = []

    for result in results:
        if not result.success:
            deduped_results.append(result)
            continue

        items = memory_dedup.filter_duplicates(result.items)

        if history_dedup:
            before_count = len(items)
            items = history_dedup.filter_sent(items)
            removed_count = before_count - len(items)
            if removed_count:
                logger.info(f"🔄 {result.source.value}: 历史去重 {removed_count} 条")

        deduped_results.append(SourceResult(
            source=result.source,
            items=items,
            success=True,
        ))

    return deduped_results, history_dedup


def count_items(results: list[SourceResult]) -> int:
    """统计成功数据源中的资讯数量。"""
    return sum(result.count for result in results if result.success)


def run_digest(
    config: Optional[dict] = None,
    *,
    enrich: bool = True,
    summarize: bool = True,
) -> DigestResult:
    """生成技术日报结果，不负责发送。"""
    config = config or get_config()

    logger.header(f"Tech Digest Daily - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"👤 GitHub 用户: {config['github_username'] or '未设置'}")
    logger.info(
        f"🤖 AI 总结: {'启用' if summarize and config['enable_ai_summary'] and config['llm_api_key'] else '禁用'}"
    )

    results = fetch_all_sources(config)
    if not any(result.success for result in results):
        raise RuntimeError("所有数据源获取失败")

    logger.section("🔄 正在去重...")
    results, history_dedup = apply_dedup(results, config)

    total_items = count_items(results)
    logger.stats(去重后内容总数=total_items)

    digest = DigestResult(
        results=results,
        ai_summary=None,
        total_items=total_items,
        history_dedup=history_dedup,
    )

    if total_items == 0:
        logger.warning("去重后无新内容")
        return digest

    if enrich:
        logger.section("🔎 正在获取深度信息...")
        try:
            enrich_results(results, config["github_token"])
        except Exception as e:
            logger.warning(f"深度信息获取失败: {e}")

    if summarize and config["enable_ai_summary"] and config["llm_api_key"]:
        logger.section("🤖 正在生成 AI 智能总结...")
        try:
            digest.ai_summary = generate_ai_summary(
                results=results,
                username=config["github_username"],
                llm_api_key=config["llm_api_key"],
                github_token=config["github_token"],
            )
            logger.info("✅ AI 总结生成成功")
            logger.stats(推荐数=len(digest.ai_summary.recommendations))
        except Exception as e:
            logger.warning(f"AI 总结生成失败: {e}")

    return digest


def mark_digest_sent(digest: DigestResult) -> None:
    """发送成功后保存历史去重记录。"""
    if not digest.history_dedup:
        return

    digest.history_dedup.mark_sent(list(digest.all_items()))
    digest.history_dedup.save()
