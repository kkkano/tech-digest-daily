"""
Tech Digest Daily - 主程序
多源技术资讯聚合 + AI 智能总结
"""

import os
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 数据模型
from models import SourceResult, AISummary

# 数据源
from sources.github_trending import GitHubTrendingSource
from sources.hackernews import HackerNewsSource
from sources.producthunt import ProductHuntSource
from sources.devto import DevToSource

# 去重
from dedup.memory import MemoryDedup
from dedup.history import HistoryDedup

# AI 总结
from ai.summarizer import generate_ai_summary

# 深度信息获取
from sources.depth_fetcher import enrich_results

# 邮件发送
from email_sender import send_digest_email


def get_config() -> dict:
    """获取配置"""
    return {
        "to_email": os.environ.get("TO_EMAIL"),
        "github_username": os.environ.get("GITHUB_USERNAME", ""),
        "llm_api_key": os.environ.get("LLM_API_KEY"),
        "github_token": os.environ.get("GITHUB_TOKEN"),

        # 数据源开关
        "enable_github": os.environ.get("ENABLE_GITHUB", "true").lower() == "true",
        "enable_hackernews": os.environ.get("ENABLE_HACKERNEWS", "true").lower() == "true",
        "enable_producthunt": os.environ.get("ENABLE_PRODUCTHUNT", "true").lower() == "true",
        "enable_devto": os.environ.get("ENABLE_DEVTO", "true").lower() == "true",

        # 数量配置
        "github_limit": int(os.environ.get("GITHUB_LIMIT", "15")),
        "hackernews_limit": int(os.environ.get("HACKERNEWS_LIMIT", "10")),
        "producthunt_limit": int(os.environ.get("PRODUCTHUNT_LIMIT", "8")),
        "devto_limit": int(os.environ.get("DEVTO_LIMIT", "10")),

        # AI 总结开关
        "enable_ai_summary": os.environ.get("ENABLE_AI_SUMMARY", "true").lower() == "true",

        # 去重开关
        "enable_history_dedup": os.environ.get("ENABLE_HISTORY_DEDUP", "true").lower() == "true",
    }


def fetch_all_sources(config: dict) -> list[SourceResult]:
    """并发获取所有数据源"""
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

    print(f"📡 正在获取 {len(sources)} 个数据源...")

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
                status = "✅" if result.success else "❌"
                count = result.count if result.success else 0
                print(f"  {status} {name}: {count} 条")
            except Exception as e:
                print(f"  ❌ {name}: 获取失败 - {e}")

    return results


def apply_dedup(results: list[SourceResult], config: dict) -> list[SourceResult]:
    """应用去重逻辑"""
    # 内存去重（同一封邮件内）
    memory_dedup = MemoryDedup()

    # 历史去重
    history_dedup = None
    if config["enable_history_dedup"]:
        history_dedup = HistoryDedup()

    deduped_results = []

    for result in results:
        if not result.success:
            deduped_results.append(result)
            continue

        items = result.items

        # 应用内存去重
        items = memory_dedup.filter_duplicates(items)

        # 应用历史去重
        if history_dedup:
            before_count = len(items)
            items = history_dedup.filter_sent(items)
            if before_count > len(items):
                print(f"  🔄 {result.source.value}: 历史去重 {before_count - len(items)} 条")

        deduped_results.append(SourceResult(
            source=result.source,
            items=items,
            success=True
        ))

    return deduped_results, history_dedup


def main():
    """主函数"""
    print("=" * 60)
    print(f"🔥 Tech Digest Daily - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 获取配置
    config = get_config()

    # 验证必要配置
    if not config["to_email"]:
        print("❌ 错误：未设置 TO_EMAIL 环境变量")
        sys.exit(1)

    print(f"📧 目标邮箱: {config['to_email']}")
    print(f"👤 GitHub 用户: {config['github_username'] or '未设置'}")
    print(f"🤖 AI 总结: {'启用' if config['enable_ai_summary'] and config['llm_api_key'] else '禁用'}")
    print("-" * 60)

    # 获取所有数据源
    results = fetch_all_sources(config)

    if not any(r.success for r in results):
        print("❌ 所有数据源获取失败")
        sys.exit(1)

    # 应用去重
    print("-" * 60)
    print("🔄 正在去重...")
    results, history_dedup = apply_dedup(results, config)

    # 统计
    total_items = sum(r.count for r in results if r.success)
    print(f"📊 去重后共 {total_items} 条内容")

    if total_items == 0:
        print("⚠️ 去重后无新内容，跳过发送")
        sys.exit(0)

    # 深度信息获取（进入仓库详情页）
    print("-" * 60)
    print("🔍 正在获取深度信息...")
    try:
        enrich_results(results, config["github_token"])
    except Exception as e:
        print(f"  ⚠️ 深度信息获取失败: {e}")

    # 生成 AI 总结
    ai_summary = None
    if config["enable_ai_summary"] and config["llm_api_key"]:
        print("-" * 60)
        print("🤖 正在生成 AI 智能总结...")
        try:
            ai_summary = generate_ai_summary(
                results=results,
                username=config["github_username"],
                llm_api_key=config["llm_api_key"],
                github_token=config["github_token"]
            )
            print(f"  ✅ AI 总结生成成功")
            print(f"  📝 推荐数: {len(ai_summary.recommendations)}")
        except Exception as e:
            print(f"  ⚠️ AI 总结生成失败: {e}")

    # 发送邮件
    print("-" * 60)
    print("📤 正在发送邮件...")
    success = send_digest_email(results, config["to_email"], ai_summary)

    # 保存历史记录
    if success and history_dedup:
        all_items = []
        for result in results:
            if result.success:
                all_items.extend(result.items)
        history_dedup.mark_sent(all_items)
        history_dedup.save()

    # 结果
    print("=" * 60)
    if success:
        print("🎉 任务完成！")
        sys.exit(0)
    else:
        print("😢 任务失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
