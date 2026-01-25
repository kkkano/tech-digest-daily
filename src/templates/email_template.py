"""
邮件模板生成器
按内容类型分类：开源项目 / 技术文章 / 新品发布
支持 Markdown 渲染，兼容主流邮件客户端
支持 Preheader 预览文本
"""

from typing import Optional
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    NewsItem, SourceResult, AISummary, SourceType,
    ContentType, CONTENT_CONFIG, SOURCE_TO_CONTENT
)

# 尝试导入 markdown，如果失败则使用简单替换
try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False


def markdown_to_email_html(text: str) -> str:
    """
    将 Markdown 转换为邮件安全的 HTML

    支持：加粗、斜体、链接、列表、换行
    """
    if not text:
        return ""

    if HAS_MARKDOWN:
        # 使用 markdown 库转换
        html = markdown.markdown(
            text,
            extensions=['nl2br']  # 换行转 <br>
        )
    else:
        # 简单的 Markdown 替换（备用方案）
        html = text
        # 加粗
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        # 斜体
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        # 链接
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
        # 换行
        html = html.replace('\n', '<br>')

    # 为转换后的元素添加内联样式（邮件必需）
    style_map = {
        '<strong>': '<strong style="color:#1a1a2e;font-weight:600;">',
        '<em>': '<em style="color:#586069;font-style:italic;">',
        '<a ': '<a style="color:#667eea;text-decoration:none;font-weight:500;" ',
        '<ul>': '<ul style="margin:12px 0;padding-left:20px;">',
        '<ol>': '<ol style="margin:12px 0;padding-left:20px;">',
        '<li>': '<li style="margin:6px 0;line-height:1.6;">',
        '<p>': '<p style="margin:10px 0;line-height:1.8;">',
    }

    for old, new in style_map.items():
        html = html.replace(old, new)

    return html


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

        # 生成 preheader 摘要文本
        preheader = self._generate_preheader(ai_summary, grouped, total_items)

        return self._wrap_layout(ai_section, sections_html, date_str, total_items, preheader)

    def _generate_preheader(
        self,
        ai_summary: Optional[AISummary],
        grouped: dict,
        total_items: int
    ) -> str:
        """
        生成邮件预览文本 (preheader)

        显示在邮件客户端的主题行下方，帮助用户快速了解邮件内容
        """
        parts = []

        # 统计各类数量
        project_count = len(grouped.get(ContentType.PROJECT, []))
        article_count = len(grouped.get(ContentType.ARTICLE, []))
        product_count = len(grouped.get(ContentType.PRODUCT, []))

        parts.append(f"今日精选 {total_items} 条")

        if project_count > 0:
            parts.append(f"{project_count} 个开源项目")
        if article_count > 0:
            parts.append(f"{article_count} 篇技术文章")
        if product_count > 0:
            parts.append(f"{product_count} 个新品发布")

        # 如果有 AI 推荐，显示 TOP1
        if ai_summary and ai_summary.recommendations:
            top1 = ai_summary.recommendations[0]
            top1_title = top1.get("title", "")[:30]
            if top1_title:
                parts.append(f"TOP1: {top1_title}")

        return " | ".join(parts)

    def _generate_ai_section(self, ai_summary: AISummary) -> str:
        """生成 AI 智能总结区块 - 支持 Markdown"""
        # 将 AI 总结转换为 HTML
        summary_html = markdown_to_email_html(ai_summary.summary)

        # 推荐列表
        recommendations_html = ""
        for i, rec in enumerate(ai_summary.recommendations[:5], 1):
            title = rec.get("title", "")
            source = rec.get("source", "")
            url = rec.get("url", "#")
            reason = rec.get("reason", "")
            highlight = rec.get("highlight", "")

            # 推荐理由也支持 Markdown
            reason_html = markdown_to_email_html(reason)

            # 高亮标签
            highlight_badge = ""
            if highlight:
                highlight_badge = f'''
                <span style="display:inline-block;background:linear-gradient(135deg,#ff6b6b,#ee5a5a);color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:500;margin-left:8px;">{highlight}</span>
                '''

            # 来源徽章颜色
            source_colors = {
                "GitHub": "#24292e",
                "GitHub Trending": "#24292e",
                "Hacker News": "#ff6600",
                "Product Hunt": "#da552f",
                "Dev.to": "#3b49df",
            }
            source_bg = source_colors.get(source, "#6a737d")

            recommendations_html += f'''
            <div style="margin-bottom:16px;padding:16px;background:linear-gradient(135deg,#fafbfc 0%,#f6f8fa 100%);border-radius:12px;border-left:4px solid #667eea;">
                <!-- 标题行 - 使用 table 布局兼容 Outlook -->
                <table cellpadding="0" cellspacing="0" border="0" width="100%">
                    <tr>
                        <td style="vertical-align:middle;width:auto;">
                            <span style="display:inline-block;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;font-weight:bold;padding:4px 12px;border-radius:6px;font-size:12px;">TOP {i}</span>
                        </td>
                        <td style="vertical-align:middle;padding-left:12px;">
                            <a href="{url}" target="_blank" style="font-weight:600;color:#0366d6;text-decoration:none;font-size:15px;line-height:1.4;">{title}</a>
                            {highlight_badge}
                        </td>
                    </tr>
                </table>
                <!-- 来源标签 -->
                <div style="margin:10px 0 8px 0;">
                    <span style="display:inline-block;background:{source_bg};color:#fff;padding:3px 10px;border-radius:4px;font-size:11px;font-weight:500;">{source}</span>
                </div>
                <!-- 推荐理由 -->
                <div style="font-size:14px;color:#24292e;line-height:1.7;">{reason_html}</div>
            </div>
            '''

        return f'''
        <div style="margin-bottom:32px;border-radius:16px;overflow:hidden;border:1px solid rgba(102,126,234,0.2);">
            <!-- 深色头部 -->
            <div style="background:linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);padding:24px;">
                <table cellpadding="0" cellspacing="0" border="0" width="100%">
                    <tr>
                        <td width="50" style="vertical-align:top;">
                            <div style="width:48px;height:48px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:12px;text-align:center;line-height:48px;font-size:26px;">
                                &#129302;
                            </div>
                        </td>
                        <td style="vertical-align:middle;padding-left:14px;">
                            <h2 style="margin:0;color:#fff;font-size:21px;font-weight:600;">AI 智能总结</h2>
                            <p style="margin:5px 0 0 0;color:rgba(255,255,255,0.75);font-size:13px;">基于你的技术偏好 + 今日热度综合分析</p>
                        </td>
                    </tr>
                </table>
            </div>

            <!-- 白色内容区 -->
            <div style="background:#ffffff;padding:24px;">
                <!-- 总结文字 -->
                <div style="font-size:15px;color:#24292e;line-height:1.9;padding:20px;background:linear-gradient(135deg,#f8f9ff 0%,#f0f4ff 100%);border-radius:12px;border:1px solid #e8ecf4;">
                    {summary_html}
                </div>

                <!-- 分隔线 -->
                <div style="height:1px;background:linear-gradient(90deg,transparent 0%,#e1e4e8 20%,#e1e4e8 80%,transparent 100%);margin:24px 0;"></div>

                <!-- 精选推荐标题 -->
                <table cellpadding="0" cellspacing="0" border="0">
                    <tr>
                        <td style="vertical-align:middle;">
                            <span style="font-size:22px;">&#127919;</span>
                        </td>
                        <td style="vertical-align:middle;padding-left:10px;">
                            <h3 style="margin:0;color:#24292e;font-size:18px;font-weight:600;">精选推荐</h3>
                        </td>
                    </tr>
                </table>

                <div style="margin-top:18px;">
                    {recommendations_html}
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
                <table cellpadding="0" cellspacing="0" border="0" width="100%">
                    <tr>
                        <td style="vertical-align:middle;">
                            <h2 style="margin:0;font-size:20px;font-weight:600;">{title}</h2>
                            <p style="margin:4px 0 0 0;opacity:0.85;font-size:13px;">{description}</p>
                        </td>
                        <td style="vertical-align:middle;text-align:right;">
                            <span style="display:inline-block;background:rgba(255,255,255,0.25);padding:6px 14px;border-radius:20px;font-size:14px;font-weight:500;">{len(items)} 条</span>
                        </td>
                    </tr>
                </table>
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
                score_html = f'<span style="color:#f1c40f;font-weight:500;">&#11088; {item.score}</span>'
            elif item.source == SourceType.HACKERNEWS:
                score_html = f'<span style="color:#ff6600;font-weight:500;">&#9650; {item.score}</span>'
            elif item.source == SourceType.PRODUCTHUNT:
                score_html = f'<span style="color:#da552f;font-weight:500;">&#11014; {item.score}</span>'
            elif item.source == SourceType.DEVTO:
                score_html = f'<span style="color:#dc2626;font-weight:500;">&#10084; {item.score}</span>'

        # 评论数
        comments_html = f'<span style="color:#6a737d;">&#128172; {item.comments}</span>' if item.comments else ""

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
                extra_html += f'<span style="display:inline-block;background:#3572A5;color:#fff;padding:2px 8px;border-radius:12px;font-size:11px;margin-right:8px;">{lang}</span>'
            if forks:
                extra_html += f'<span style="color:#6a737d;margin-right:8px;">&#127860; {forks}</span>'
            if stars_today:
                extra_html += f'<span style="color:#28a745;font-weight:500;">&#128200; +{stars_today} today</span>'

        elif item.source == SourceType.DEVTO:
            tags = item.extra.get("tags", [])[:3]
            reading_time = item.extra.get("reading_time", 0)
            if tags:
                extra_html += " ".join([f'<span style="display:inline-block;background:#e8e8e8;color:#333;padding:2px 6px;border-radius:4px;font-size:10px;margin-right:4px;">#{tag}</span>' for tag in tags])
            if reading_time:
                extra_html += f'<span style="color:#6a737d;margin-left:8px;">&#9201; {reading_time} min</span>'

        # 深度信息（如果有）
        depth_html = ""
        if item.readme_summary:
            readme_text = markdown_to_email_html(item.readme_summary[:150] + "...")
            depth_html = f'''
            <div style="margin-top:12px;padding:12px;background:linear-gradient(135deg,#f0f7ff 0%,#e8f4fd 100%);border-radius:8px;font-size:12px;color:#0366d6;border-left:3px solid #0366d6;">
                <strong>&#128214; README:</strong> {readme_text}
            </div>
            '''
        if item.tech_stack:
            tech_str = " &bull; ".join(item.tech_stack[:5])
            depth_html += f'''
            <div style="margin-top:8px;font-size:11px;color:#6a737d;">
                <strong>&#128736; 技术栈:</strong> {tech_str}
            </div>
            '''

        # 作者信息
        author_html = f'<span style="color:#6a737d;">by {item.author}</span>' if item.author else ""

        return f'''
        <div style="margin-bottom:16px;border:1px solid #e1e4e8;border-radius:12px;overflow:hidden;background:#fafbfc;">
            {image_html}
            <div style="padding:16px;">
                <div style="margin-bottom:10px;">
                    <a href="{url}" target="_blank" style="font-size:16px;font-weight:600;color:#0366d6;text-decoration:none;line-height:1.4;">{title}</a>
                </div>
                <p style="color:#586069;margin:0 0 12px 0;font-size:14px;line-height:1.6;">{desc}</p>
                {depth_html}
                <!-- 元信息行 - 使用 table 兼容 -->
                <table cellpadding="0" cellspacing="0" border="0" style="margin-top:14px;">
                    <tr>
                        <td style="vertical-align:middle;padding-right:10px;">
                            <span style="display:inline-block;background:{bg_color};color:{text_color};padding:3px 10px;border-radius:6px;font-size:11px;font-weight:500;">{source_name}</span>
                        </td>
                        <td style="vertical-align:middle;padding-right:10px;">{score_html}</td>
                        <td style="vertical-align:middle;padding-right:10px;">{comments_html}</td>
                        <td style="vertical-align:middle;">{author_html}</td>
                    </tr>
                </table>
                <div style="margin-top:10px;">
                    {extra_html}
                </div>
            </div>
        </div>
        '''

    def _wrap_layout(self, ai_section: str, sections_html: str, date_str: str, total_items: int, preheader: str = "") -> str:
        """包装整体布局 - 兼容主流邮件客户端"""
        # Preheader HTML - 隐藏的预览文本
        preheader_html = ""
        if preheader:
            # 使用隐藏的 div + 空白填充，确保预览文本显示正确
            preheader_html = f'''
    <!-- Preheader 预览文本 -->
    <div style="display:none;font-size:1px;color:#f0f2f5;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;">
        {preheader}
        {"&nbsp;&zwnj;" * 50}
    </div>
'''

        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>技术日报 - {date_str}</title>
    <!--[if mso]>
    <style type="text/css">
        table {{border-collapse:collapse;border-spacing:0;margin:0;}}
        div, td {{padding:0;}}
        div {{margin:0 !important;}}
    </style>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
    <style type="text/css">
        /* 基础重置 */
        body, table, td, p, a, li {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
        table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
        img {{ -ms-interpolation-mode: bicubic; }}

        /* 移动端适配 */
        @media only screen and (max-width: 620px) {{
            .email-container {{
                width: 100% !important;
                max-width: 100% !important;
            }}
            .email-padding {{
                padding: 12px !important;
            }}
            .header-title {{
                font-size: 26px !important;
            }}
            .mobile-padding {{
                padding: 14px !important;
            }}
        }}
    </style>
</head>
<body style="margin:0;padding:0;background-color:#f0f2f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased;">
    {preheader_html}
    <!-- 外层容器 -->
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:#f0f2f5;">
        <tr>
            <td align="center" style="padding:20px;" class="email-padding">
                <!-- 内容容器 -->
                <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="700" class="email-container" style="max-width:700px;width:100%;">
                    <tr>
                        <td>
                            <!-- 头部 -->
                            <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 50%,#f093fb 100%);color:#fff;padding:36px 32px;border-radius:20px 20px 0 0;text-align:center;">
                                <h1 style="margin:0 0 8px 0;font-size:32px;font-weight:700;" class="header-title">&#128293; 技术日报</h1>
                                <p style="margin:0;opacity:0.95;font-size:18px;">{date_str}</p>
                                <p style="margin:14px 0 0 0;opacity:0.85;font-size:14px;">
                                    &#128202; 今日精选 <strong>{total_items}</strong> 条内容
                                    &nbsp;&bull;&nbsp;
                                    开源项目 / 技术文章 / 新品发布
                                </p>
                            </div>

                            <!-- 主体内容 -->
                            <div style="background:#f6f8fa;padding:28px;border-radius:0 0 20px 20px;" class="mobile-padding">

                                {ai_section}

                                {sections_html}

                                <!-- 页脚 -->
                                <div style="text-align:center;margin-top:36px;padding-top:24px;border-top:1px solid #e1e4e8;">
                                    <p style="color:#959da5;font-size:13px;margin:0;line-height:1.8;">
                                        由 <strong style="color:#667eea;">Tech Digest Daily</strong> 自动生成<br>
                                        <a href="https://github.com/kkkano/github-trending-daily" target="_blank" style="color:#0366d6;text-decoration:none;">GitHub</a>
                                        &nbsp;|&nbsp;
                                        数据来源: GitHub &bull; Hacker News &bull; Product Hunt &bull; Dev.to
                                    </p>
                                </div>
                            </div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
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
        summary="今日技术圈热点聚焦在 **AI 编程工具**和开发者效率提升上。VS Code 持续霸榜，而 *AI 驱动的代码编辑器*正在快速崛起。\n\n值得注意的是，**Cursor** 获得了大量关注，它代表了下一代 IDE 的发展方向。",
        recommendations=[
            {"title": "Cursor AI", "source": "Product Hunt", "url": "https://example.com", "reason": "非常**火爆**的 AI 编程工具，即使你没有 AI 背景也值得关注。它能够*显著提升*编码效率。", "highlight": "🔥 爆款"},
            {"title": "VS Code", "source": "GitHub", "url": "https://github.com/microsoft/vscode", "reason": "与你的 **TypeScript** 技术栈高度匹配，是目前最流行的编辑器。"}
        ]
    )

    html = template.generate(test_results, "2025年01月25日", test_summary)
    with open("test_email.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("测试邮件已生成: test_email.html")
