"""
邮件模板生成器
按内容类型分类：开源项目 / 技术文章 / 新品发布
来源显示在每个条目的下标位置
"""

from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    NewsItem, SourceResult, AISummary, SourceType,
    ContentType, CONTENT_CONFIG, SOURCE_TO_CONTENT
)


class EmailTemplate:
    """邮件模板生成器 - 按内容类型分类"""

    def generate(
        self,
        results: list[SourceResult],
        date_str: str,
        ai_summary: Optional[AISummary] = None
    ) -> str:
        """
        生成完整的邮件 HTML

        Args:
            results: 各数据源的结果列表
            date_str: 日期字符串
            ai_summary: AI 智能总结（可选）

        Returns:
            完整的 HTML 字符串
        """
        # 合并所有 items 并按内容类型分组
        all_items = []
        for result in results:
            if result.success:
                all_items.extend(result.items)

        # 按内容类型分组
        grouped = {
            ContentType.PROJECT: [],
            ContentType.ARTICLE: [],
            ContentType.PRODUCT: [],
        }
        for item in all_items:
            grouped[item.content_type].append(item)

        # 生成 AI 总结区块
        ai_section = self._generate_ai_section(ai_summary) if ai_summary else ""

        # 按顺序生成各类型区块：项目 -> 文章 -> 产品
        sections_html = ""
        for content_type in [ContentType.PROJECT, ContentType.ARTICLE, ContentType.PRODUCT]:
            items = grouped[content_type]
            if items:
                sections_html += self._generate_content_section(content_type, items)

        # 统计信息
        total_items = len(all_items)

        return self._wrap_layout(ai_section, sections_html, date_str, total_items)

    def _generate_ai_section(self, ai_summary: AISummary) -> str:
        """生成 AI 智能总结区块"""
        # 推荐列表
        recommendations_html = ""
        for i, rec in enumerate(ai_summary.recommendations[:5], 1):
            title = rec.get("title", "")
            source = rec.get("source", "")
            url = rec.get("url", "#")
            reason = rec.get("reason", "")
            highlight = rec.get("highlight", "")  # 重点标签

            highlight_badge = ""
            if highlight:
                highlight_badge = f'<span style="background:#ff6b6b;color:#fff;padding:2px 6px;border-radius:4px;font-size:10px;margin-left:6px;">{highlight}</span>'

            recommendations_html += f'''
            <div style="margin-bottom:16px;padding:14px;background:#f8f9fa;border-radius:10px;border-left:4px solid #667eea;">
                <div style="display:flex;align-items:center;margin-bottom:8px;flex-wrap:wrap;">
                    <span style="background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;font-weight:bold;padding:3px 10px;border-radius:6px;font-size:12px;margin-right:10px;">TOP {i}</span>
                    <a href="{url}" target="_blank" style="font-weight:600;color:#0366d6;text-decoration:none;font-size:15px;">{title}</a>
                    {highlight_badge}
                </div>
                <div style="font-size:12px;color:#6a737d;margin-bottom:6px;">
                    <span style="background:#e8e8e8;padding:2px 6px;border-radius:4px;">{source}</span>
                </div>
                <div style="font-size:14px;color:#24292e;line-height:1.6;">{reason}</div>
            </div>
            '''

        return f'''
        <div style="margin-bottom:32px;background:linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);border-radius:16px;overflow:hidden;">
            <div style="padding:24px;">
                <div style="display:flex;align-items:center;margin-bottom:16px;">
                    <span style="font-size:32px;margin-right:12px;">🤖</span>
                    <div>
                        <h2 style="margin:0;color:#fff;font-size:22px;">AI 智能总结</h2>
                        <p style="margin:4px 0 0 0;color:rgba(255,255,255,0.7);font-size:13px;">基于你的技术偏好 + 今日热度综合分析</p>
                    </div>
                </div>
                <div style="background:rgba(255,255,255,0.98);border-radius:12px;padding:20px;">
                    <div style="font-size:15px;color:#24292e;line-height:1.9;margin-bottom:20px;padding:16px;background:#f6f8fa;border-radius:8px;">
                        {ai_summary.summary}
                    </div>
                    <div style="border-top:1px solid #e1e4e8;padding-top:16px;">
                        <h3 style="margin:0 0 14px 0;color:#24292e;font-size:17px;display:flex;align-items:center;">
                            <span style="margin-right:8px;">🎯</span> 精选推荐
                        </h3>
                        {recommendations_html}
                    </div>
                </div>
            </div>
        </div>
        '''

    def _generate_content_section(self, content_type: ContentType, items: list[NewsItem]) -> str:
        """生成单个内容类型区块"""
        config = CONTENT_CONFIG.get(content_type, {})
        title = config.get("title", "内容")
        gradient = config.get("gradient", "linear-gradient(135deg, #667eea 0%, #764ba2 100%)")
        description = config.get("description", "")

        # 生成项目卡片
        items_html = ""
        for item in items:
            items_html += self._generate_item_card(item)

        return f'''
        <div style="margin-bottom:28px;">
            <div style="background:{gradient};color:#fff;padding:18px 22px;border-radius:14px 14px 0 0;">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div>
                        <h2 style="margin:0;font-size:20px;font-weight:600;">{title}</h2>
                        <p style="margin:4px 0 0 0;opacity:0.85;font-size:13px;">{description}</p>
                    </div>
                    <span style="background:rgba(255,255,255,0.25);padding:6px 14px;border-radius:20px;font-size:14px;font-weight:500;">{len(items)} 条</span>
                </div>
            </div>
            <div style="background:#fff;border:1px solid #e1e4e8;border-top:none;border-radius:0 0 14px 14px;padding:18px;">
                {items_html}
            </div>
        </div>
        '''

    def _generate_item_card(self, item: NewsItem) -> str:
        """生成单个内容卡片 - 统一样式，来源显示在下标"""
        # 来源徽章颜色
        source_colors = {
            SourceType.GITHUB: ("#24292e", "#fff"),
            SourceType.HACKERNEWS: ("#ff6600", "#fff"),
            SourceType.PRODUCTHUNT: ("#da552f", "#fff"),
            SourceType.DEVTO: ("#3b49df", "#fff"),
        }
        bg_color, text_color = source_colors.get(item.source, ("#6a737d", "#fff"))

        # 基础信息
        title = item.title
        desc = item.description_cn or item.description
        url = item.url
        source_name = item.source_display

        # 热度信息
        score_html = ""
        if item.score:
            if item.source == SourceType.GITHUB:
                score_html = f'<span style="color:#f1c40f;">⭐ {item.score}</span>'
            elif item.source == SourceType.HACKERNEWS:
                score_html = f'<span style="color:#ff6600;">▲ {item.score}</span>'
            elif item.source == SourceType.PRODUCTHUNT:
                score_html = f'<span style="color:#da552f;">⬆ {item.score}</span>'
            elif item.source == SourceType.DEVTO:
                score_html = f'<span style="color:#dc2626;">❤ {item.score}</span>'

        # 评论数
        comments_html = f'<span style="color:#6a737d;">💬 {item.comments}</span>' if item.comments else ""

        # 图片（可选）
        image_html = ""
        if item.image_url and item.source in [SourceType.GITHUB, SourceType.PRODUCTHUNT]:
            image_html = f'''
            <a href="{url}" target="_blank" style="display:block;margin-bottom:12px;">
                <img src="{item.image_url}" alt="{title}" style="width:100%;height:auto;border-radius:8px;display:block;">
            </a>
            '''

        # 额外信息（根据类型）
        extra_html = ""
        if item.source == SourceType.GITHUB:
            lang = item.extra.get("language", "")
            forks = item.extra.get("forks", "")
            stars_today = item.extra.get("stars_today", "")

            if lang:
                extra_html += f'<span style="background:#3572A5;color:#fff;padding:2px 8px;border-radius:12px;font-size:11px;">{lang}</span>'
            if forks:
                extra_html += f'<span style="color:#6a737d;margin-left:8px;">🍴 {forks}</span>'
            if stars_today:
                extra_html += f'<span style="color:#28a745;margin-left:8px;font-weight:500;">📈 +{stars_today} today</span>'

        elif item.source == SourceType.DEVTO:
            tags = item.extra.get("tags", [])[:3]
            reading_time = item.extra.get("reading_time", 0)
            if tags:
                extra_html += " ".join([f'<span style="background:#e8e8e8;color:#333;padding:2px 6px;border-radius:4px;font-size:10px;">#{tag}</span>' for tag in tags])
            if reading_time:
                extra_html += f'<span style="color:#6a737d;margin-left:8px;">⏱️ {reading_time} min</span>'

        # 深度信息（如果有）
        depth_html = ""
        if item.readme_summary:
            depth_html = f'''
            <div style="margin-top:10px;padding:10px;background:#f0f7ff;border-radius:6px;font-size:12px;color:#0366d6;border-left:3px solid #0366d6;">
                <strong>📖 README 摘要:</strong> {item.readme_summary[:150]}...
            </div>
            '''
        if item.tech_stack:
            tech_str = " • ".join(item.tech_stack[:5])
            depth_html += f'''
            <div style="margin-top:8px;font-size:11px;color:#6a737d;">
                <strong>🛠️ 技术栈:</strong> {tech_str}
            </div>
            '''

        # 作者信息
        author_html = f'<span style="color:#6a737d;">by {item.author}</span>' if item.author else ""

        return f'''
        <div style="margin-bottom:16px;border:1px solid #e1e4e8;border-radius:10px;overflow:hidden;background:#fafbfc;transition:box-shadow 0.2s;">
            {image_html}
            <div style="padding:14px;">
                <div style="margin-bottom:8px;">
                    <a href="{url}" target="_blank" style="font-size:16px;font-weight:600;color:#0366d6;text-decoration:none;line-height:1.4;">{title}</a>
                </div>
                <p style="color:#586069;margin:0 0 10px 0;font-size:14px;line-height:1.6;">{desc}</p>
                {depth_html}
                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-top:12px;font-size:12px;">
                    <span style="background:{bg_color};color:{text_color};padding:3px 8px;border-radius:6px;font-size:11px;font-weight:500;">{source_name}</span>
                    {score_html}
                    {comments_html}
                    {author_html}
                </div>
                <div style="margin-top:8px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                    {extra_html}
                </div>
            </div>
        </div>
        '''

    def _wrap_layout(self, ai_section: str, sections_html: str, date_str: str, total_items: int) -> str:
        """包装整体布局"""
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>技术日报 - {date_str}</title>
</head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',Helvetica,Arial,sans-serif;background-color:#f0f2f5;margin:0;padding:20px;">
    <div style="max-width:700px;margin:0 auto;">
        <!-- 头部 -->
        <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 50%,#f093fb 100%);color:#fff;padding:36px 32px;border-radius:20px 20px 0 0;text-align:center;">
            <h1 style="margin:0 0 8px 0;font-size:32px;font-weight:700;">🔥 技术日报</h1>
            <p style="margin:0;opacity:0.95;font-size:18px;">{date_str}</p>
            <p style="margin:12px 0 0 0;opacity:0.8;font-size:14px;">
                📊 今日精选 <strong>{total_items}</strong> 条内容
                <span style="margin:0 8px;">•</span>
                开源项目 / 技术文章 / 新品发布
            </p>
        </div>

        <!-- 主体内容 -->
        <div style="background:#f6f8fa;padding:28px;border-radius:0 0 20px 20px;">

            {ai_section}

            {sections_html}

            <!-- 页脚 -->
            <div style="text-align:center;margin-top:36px;padding-top:24px;border-top:1px solid #e1e4e8;">
                <p style="color:#959da5;font-size:13px;margin:0;line-height:1.8;">
                    由 <strong style="color:#667eea;">Tech Digest Daily</strong> 自动生成<br>
                    <a href="https://github.com/kkkano/github-trending-daily" target="_blank" style="color:#0366d6;">GitHub</a>
                    <span style="margin:0 6px;color:#d1d5da;">|</span>
                    数据来源: GitHub · Hacker News · Product Hunt · Dev.to
                </p>
            </div>
        </div>
    </div>
</body>
</html>
        '''


if __name__ == "__main__":
    # 测试
    template = EmailTemplate()

    # 创建测试数据
    from models import NewsItem, SourceResult, AISummary, SourceType

    test_items = [
        NewsItem(
            source=SourceType.GITHUB,
            title="microsoft/vscode",
            url="https://github.com/microsoft/vscode",
            description="Visual Studio Code",
            description_cn="Visual Studio Code - 一个轻量级但功能强大的代码编辑器",
            score=165000,
            rank=1,
            extra={"language": "TypeScript", "stars": "165k", "forks": "29k", "stars_today": "521"}
        ),
        NewsItem(
            source=SourceType.HACKERNEWS,
            title="The Rise of AI in Software Development",
            url="https://example.com/ai-dev",
            description="How AI is changing the way we write code",
            description_cn="AI 如何改变我们编写代码的方式",
            score=450,
            comments=123
        ),
        NewsItem(
            source=SourceType.PRODUCTHUNT,
            title="Cursor AI",
            url="https://www.producthunt.com/posts/cursor-ai",
            description="AI-first code editor",
            description_cn="AI 优先的代码编辑器",
            score=1200,
            comments=89,
            image_url="https://ph-files.imgix.net/cursor.png"
        ),
    ]

    test_results = [
        SourceResult(source=SourceType.GITHUB, items=[test_items[0]], success=True),
        SourceResult(source=SourceType.HACKERNEWS, items=[test_items[1]], success=True),
        SourceResult(source=SourceType.PRODUCTHUNT, items=[test_items[2]], success=True),
    ]

    test_summary = AISummary(
        summary="今日技术圈热点聚焦在 AI 编程工具和开发者效率提升上。VS Code 持续霸榜，而 AI 驱动的代码编辑器正在快速崛起。",
        recommendations=[
            {"title": "Cursor AI", "source": "Product Hunt", "url": "https://example.com", "reason": "非常火爆的 AI 编程工具，即使你没有 AI 背景也值得关注", "highlight": "🔥 爆款"},
            {"title": "VS Code", "source": "GitHub", "url": "https://github.com/microsoft/vscode", "reason": "与你的 TypeScript 技术栈高度匹配"}
        ]
    )

    html = template.generate(test_results, "2025年01月25日", test_summary)
    with open("test_email.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("测试邮件已生成: test_email.html")
