"""
AI 智能总结生成器
根据用户偏好 + 热度综合分析，生成个性化的技术日报总结
"""

import json
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import NewsItem, SourceResult, AISummary, UserProfile, SourceType
from ai.llm_client import LLMClient
from ai.github_profile import GitHubProfileFetcher


class AISummarizer:
    """AI 智能总结生成器"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        初始化

        Args:
            llm_client: LLM 客户端实例
        """
        self.llm_client = llm_client or LLMClient()

    def generate_summary(
        self,
        results: list[SourceResult],
        user_profile: Optional[UserProfile] = None
    ) -> AISummary:
        """
        生成智能总结

        Args:
            results: 各数据源的结果列表
            user_profile: 用户偏好数据（可选）

        Returns:
            AISummary 对象
        """
        # 构建 prompt
        prompt = self._build_prompt(results, user_profile)

        # 调用 LLM
        try:
            response = self.llm_client.chat_json(prompt, temperature=0.7)
            return AISummary.from_dict(response)
        except Exception as e:
            print(f"AI 总结生成失败: {e}")
            # 返回默认总结
            return AISummary(
                summary="今日技术资讯已为您整理完毕，请查看下方详细内容。",
                recommendations=[]
            )

    def _build_prompt(
        self,
        results: list[SourceResult],
        user_profile: Optional[UserProfile] = None
    ) -> str:
        """构建 LLM Prompt - 平衡个性化与热度"""

        # 用户偏好部分
        user_section = ""
        if user_profile:
            interests = user_profile.get_interests_summary()
            user_section = f"""
## 用户背景参考（仅作参考，不要完全依赖）

- **GitHub 用户名**: {user_profile.username}
- **常用编程语言**: {', '.join(interests['top_languages'][:5]) or '未知'}
- **感兴趣的技术领域**: {', '.join(interests['top_topics'][:10]) or '未知'}
- **Star 过的仓库数**: {interests['starred_count']}

### 最近 Star 的仓库（代表兴趣方向）:
{self._format_starred_repos(user_profile.starred_repos[:8])}

⚠️ **重要提示**: 用户背景仅作为参考之一。如果有非常火爆或具有重大影响力的项目/文章，即使与用户背景无关，也应该推荐！
"""

        # 资讯内容部分 - 包含热度信息
        content_sections = []
        for result in results:
            if result.success and result.items:
                section = self._format_source_items_with_score(result)
                content_sections.append(section)

        content_section = "\n\n".join(content_sections)

        # 计算热度阈值
        hot_threshold = self._calculate_hot_threshold(results)

        # 完整 Prompt
        prompt = f"""你是一位资深的技术资讯编辑，擅长分析技术趋势并为读者提供有价值的推荐。

{user_section}

## 今日资讯内容

{content_section}

---

## 你的任务

### 1. 今日技术圈总结（150-250字）

请用专业但易懂的中文总结今日技术圈的主要趋势和热点，包括：
- 最火爆的项目/产品（热度最高的那几个）
- 技术圈的重要动态和趋势
- 值得关注的新兴技术或工具

**写作风格**: 像一位懂技术的朋友在和你聊天，既专业又有趣，可以适当加入一些观点。

### 2. 精选推荐 TOP 5

**推荐标准（重要！按优先级排序）**:

1. **🔥 超高热度**（热度分数 > {hot_threshold}）: 无论是否匹配用户背景，这种现象级内容必须推荐
2. **📈 显著增长**: 今日新增 stars/votes 特别多的项目
3. **🎯 用户匹配**: 与用户技术栈或兴趣相关的高质量内容
4. **💡 行业影响**: 可能改变行业或工作方式的重要项目/文章
5. **🆕 创新突破**: 解决重要问题或带来新方法的内容

**分配建议**:
- 至少 1-2 个"必看"级别的热门内容（即使与用户背景无关）
- 2-3 个与用户背景相关的个性化推荐
- 至少 1 个可能开阔视野的跨领域推荐

每个推荐需包含：
- **title**: 项目/文章名称
- **source**: 来源平台（GitHub / Hacker News / Product Hunt / Dev.to）
- **url**: 原始 URL
- **reason**: 推荐理由（说明为什么值得关注，如果是热门内容要强调其火爆程度）
- **highlight**: 特殊标签（可选，如 "🔥 爆款"、"📈 飙升"、"💎 宝藏"、"🚀 必看"、"🎯 为你推荐" 等）

### 输出格式

请严格按照以下 JSON 格式输出，不要添加任何额外文字：

```json
{{
  "summary": "今日技术圈总结内容...",
  "recommendations": [
    {{
      "title": "项目/文章标题",
      "source": "来源平台",
      "url": "链接地址",
      "reason": "推荐理由",
      "highlight": "特殊标签（可选）"
    }},
    ...
  ]
}}
```
"""
        return prompt

    def _calculate_hot_threshold(self, results: list[SourceResult]) -> int:
        """计算热度阈值（用于识别超高热度内容）"""
        all_scores = []
        for result in results:
            if result.success:
                for item in result.items:
                    if item.score:
                        all_scores.append(item.score)

        if not all_scores:
            return 1000

        # 使用 75 分位数作为"热门"阈值
        sorted_scores = sorted(all_scores, reverse=True)
        idx = max(0, len(sorted_scores) // 4)
        return sorted_scores[idx] if idx < len(sorted_scores) else sorted_scores[0]

    def _format_starred_repos(self, repos: list[dict]) -> str:
        """格式化 Star 的仓库列表"""
        if not repos:
            return "暂无数据"

        lines = []
        for repo in repos[:8]:
            name = repo.get("name", "")
            desc = repo.get("description", "")[:50] if repo.get("description") else ""
            lang = repo.get("language", "")
            lines.append(f"- {name} ({lang}): {desc}")

        return "\n".join(lines)

    def _format_source_items_with_score(self, result: SourceResult) -> str:
        """格式化单个数据源的内容 - 包含热度分数"""
        source_names = {
            SourceType.GITHUB: "GitHub Trending",
            SourceType.HACKERNEWS: "Hacker News",
            SourceType.PRODUCTHUNT: "Product Hunt",
            SourceType.DEVTO: "Dev.to"
        }

        name = source_names.get(result.source, str(result.source))
        lines = [f"### {name} ({len(result.items)} 条)"]

        for i, item in enumerate(result.items[:15], 1):
            title = item.title
            desc = item.description_cn or item.description
            desc = desc[:120] + "..." if len(desc) > 120 else desc
            url = item.url

            # 热度指标
            score_str = ""
            if item.score:
                if result.source == SourceType.GITHUB:
                    stars_today = item.extra.get("stars_today", "")
                    score_str = f"⭐ {item.score}"
                    if stars_today:
                        score_str += f" (今日 +{stars_today})"
                elif result.source == SourceType.HACKERNEWS:
                    score_str = f"🔺 {item.score} points"
                elif result.source == SourceType.PRODUCTHUNT:
                    score_str = f"⬆️ {item.score} votes"
                elif result.source == SourceType.DEVTO:
                    score_str = f"❤️ {item.score} reactions"

            # 深度信息
            depth_info = ""
            if item.readme_summary:
                depth_info += f"\n   📖 README: {item.readme_summary[:100]}..."
            if item.tech_stack:
                depth_info += f"\n   🛠️ 技术栈: {', '.join(item.tech_stack[:5])}"

            lines.append(f"{i}. **{title}** {score_str}")
            lines.append(f"   {desc}")
            lines.append(f"   链接: {url}")
            if depth_info:
                lines.append(depth_info)

        return "\n".join(lines)


def generate_ai_summary(
    results: list[SourceResult],
    username: Optional[str] = None,
    llm_api_key: Optional[str] = None,
    github_token: Optional[str] = None
) -> AISummary:
    """
    便捷函数：生成 AI 智能总结

    Args:
        results: 数据源结果列表
        username: GitHub 用户名（用于个性化推荐）
        llm_api_key: LLM API Key
        github_token: GitHub Token

    Returns:
        AISummary 对象
    """
    # 初始化 LLM 客户端
    llm_client = LLMClient(api_key=llm_api_key)

    # 获取用户偏好
    user_profile = None
    if username:
        try:
            print(f"  📊 正在获取 {username} 的 GitHub 偏好数据...")
            fetcher = GitHubProfileFetcher(token=github_token)
            user_profile = fetcher.get_user_profile(username)
            print(f"  ✅ 已获取用户偏好数据")
        except Exception as e:
            print(f"  ⚠️ 获取用户偏好失败: {e}")

    # 生成总结
    summarizer = AISummarizer(llm_client)
    return summarizer.generate_summary(results, user_profile)


if __name__ == "__main__":
    # 测试
    from sources.hackernews import HackerNewsSource

    # 获取一些测试数据
    hn = HackerNewsSource()
    hn_result = hn.fetch(limit=5)

    if hn_result.success:
        print("正在生成 AI 总结...")
        summary = generate_ai_summary(
            results=[hn_result],
            username="kkkano"
        )
        print(f"\n总结:\n{summary.summary}")
        print(f"\n推荐数: {len(summary.recommendations)}")
        for rec in summary.recommendations:
            highlight = rec.get('highlight', '')
            print(f"- {highlight} {rec.get('title')}: {rec.get('reason')}")
